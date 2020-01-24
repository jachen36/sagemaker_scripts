import boto3
import click
from datetime import datetime
import json
import logging
from pathlib import Path
from notebook import notebookapp
import requests

log_fn = 'autostop.log'
datetime_format = '%Y-%m-%d %H:%M:%S'
datetime_parse = "%Y-%m-%dT%H:%M:%S.%fz"

# TODO: Remove for testing
port = 1234
idle_time = 3300
ignore_connections = False
log_level = 'DEBUG'  

def get_time_diff(last_activity):
    """Return the time differences in seconds"""
    last_activity = datetime.strptime(last_activity, datetime_parse)
    return (datetime.utcnow() - last_activity).total_seconds()

def get_notebook_name():
    """Get Sagemaker ID"""
    log_path = '/opt/ml/metadata/resource-metadata.json'
    with open(log_path, 'r') as logs:
        _logs = json.load(logs)
    return _logs['ResourceName']

def log_time():
    """Return the str for current UTC time"""
    return datetime.utcnow().strftime(datetime_format) + ' UTC'

def get_jupyter_info():
    """Return a list of active notebooks in jupyter server"""
    # assume there is only 1 jupyter session on server
    server_info = list(notebookapp.list_running_servers())[0]  # [s1] get server info
    headers = {'Authorization': 'token ' + server_info['token'], 
               'Connection':'close'}  # [s3] to be safe
    response = requests.get(server_info['url'] + 'api/sessions',  # [s4] sessions has more info than api/kernels
                            headers=headers, 
                            verify=False)  # [s5] do not verify ssl ceritificates
    return response.json()  # return a list of active notebooks if any


# TODO: Create helper functions instead of doing this. 
def is_idle(data, idle_max, ignore_connections):
    """Determine if jupyter is idle based on inputs"""
    idle_min = idle_max
    idle = True
    for notebook in data:
        # Idleness is defined by Jupyter [s6]
        kernel_info = notebook.get('kernel', {})
        # As long as there is atleast 1 active notebook
        if kernel_info.get('execution_state') == 'busy':
            idle = False
        
        # As long as someone is connected to a notebook
        if not ignore_connections & kernel_info.get('connections', 0) > 0:
            idle = False
        
        # idle in seconds based on the latest activity for all notebook
        if kernel_info.get('execution_state') == 'idle':
            idle_min = min(get_time_diff(notebook), idle_min)
            if idle_min >= idle_max:
                idle = False
        
        # No need to further check if there is at least one active condition
        if not idle:
            break
        
    return idle




# TODO: Add override for office hours? and maybe work days?
@click.command()
@click.option(  # TODO: Remove this. server info should have this?
    '--port', '-p',
    default='8443',
    help='port number of the jupyter server. default is 8443'
)
@click.option(
    '--idle-time', '-t',
    default=3600,
    help='Auto stop time in seconds. default 1 hour'
)
@click.option(
    '--ignore-connections',
    is_flag=True,
    help='Stop notebook once idle, ignore connected users'
)
@click.option(
    '--log-level',
    default='DEBUG',  # TODO: Change this to INFO
    help='Logging Level between DEBUG and INFO. default is INFO'
)
def main(port, idle_time, ignore_connections, log_level):
    logging.basicConfig(filename=log_fn,
                        format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)  # [s7]
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    logger.setLevel(level=numeric_level)
    logger.info(log_time() + ' AutoStop Script Starts')
    logger.debug(f'Parameters: port {port}, idle_time {idle_time}, ignore_connections {ignore_connections}')


    # get server info
    # test if idle
    # if idle shutdown
    # if not do nothing and log it

    data = get_jupyter_info()
    logger.info(f'Number of kernels: {len(data)}')
        
    if len(data) > 0:
        if log_level == 'DEBUG':
            logger.debug(log_time() + ' Jupyter Kernels Info')
            for notebook in data:
                logger.debug((f"name: {notebook.get('path')}, "
                               f"state: {notebook.get('kernel').get('execution_state')}, "
                               f"last: {notebook.get('kernel').get('last_activity')}"))

    # now need to find if server is idle

    # Use case is when SageMaker first launch with has zero active notebooks so need to give it some time
    # Also it will shutdown once all notebooks are closed. 
    else:
        # simplier way could be just 
        client = boto3.client('sagemaker')
        uptime = client.describe_notebook_instance(
            NotebookInstanceName=get_notebook_name()
        )['LastModifiedTime']  # sagemaker internal time is utc
        # Bug? This will shutdown once there are zero notebook. If you just happens to close
        # everything during the time cron checks, it will shutdown..
        if not is_idle(uptime.strftime("%Y-%m-%dT%H:%M:%S.%fz")):
            idle = False

            
    # TODO: Add the ability to have psutil cpu/gpu monitoring? Just in case script is using terminal instead
            # simple way is just to do monitoring of cpu/gpu for the next ten minutes if below then shut down. 
            # should record idle sttate to see how much is being used...
    if idle:
        client = boto3.client('sagemaker')
        client.stop_notebook_instance(
            NotebookInstanceName=get_notebook_name()
        )


if __name__ == "__main__":
    main()



# source
# [s1] https://github.com/jupyter/notebook/blob/f354740e57f206d67bfb077a9f23bb8d22b6b311/notebook/notebookapp.py#L413
# [s2] https://github.com/aws-samples/amazon-sagemaker-notebook-instance-lifecycle-config-samples/blob/master/scripts/auto-stop-idle/autostop.py
# [s3] https://stackoverflow.com/a/15511852
# [s4] https://github.com/jupyter/jupyter/wiki/Jupyter-Notebook-Server-API#Sessions-API
# [s5] https://requests.readthedocs.io/en/master/user/advanced/
# [s6] https://github.com/jupyter/notebook/issues/4634
# [s7] https://stackoverflow.com/a/35326281
















