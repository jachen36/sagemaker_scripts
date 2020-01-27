import boto3
import click
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from notebook import notebookapp
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
log_fn = 'autostop.log'
datetime_format = '%Y-%m-%d %H:%M:%S'
datetime_parse = "%Y-%m-%dT%H:%M:%S.%fz"

def str_to_datetime(dt):
    """Parse str to datetime"""
    return datetime.strptime(dt, datetime_parse)

def get_time_diff(last_activity):
    """Return the time differences in seconds"""
    last_activity = str_to_datetime(last_activity)
    return int((datetime.utcnow() - last_activity).total_seconds())

def get_notebook_name():
    """Get Sagemaker ID"""
    log_path = '/opt/ml/metadata/resource-metadata.json'
    with open(log_path, 'r') as logs:
        _logs = json.load(logs)
    return _logs['ResourceName']

def log_time():
    """Return the str for current UTC time"""
    return datetime.utcnow().isoformat(' ', 'seconds') + ' UTC'

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

def is_idle(data, timeout, ignore_connections):
    """Determine if jupyter is idle based on inputs"""
    idle_ls, idle_time, conn_ls = [], [], []

    for notebook in data:
        # Idleness is defined by Jupyter [s6]
        kernel_info = notebook.get('kernel', {})

        idle_ls.append(kernel_info.get('execution_state') == 'idle')
        idle_time.append(get_time_diff(kernel_info.get('last_activity')) >= timeout)
        conn_ls.append(kernel_info.get('connections', 0) == 0)  
        
    return all(idle_ls) and all(idle_time) and (ignore_connections or all(conn_ls))

@click.command()
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
    default='DEBUG',
    help='Logging Level between DEBUG and INFO. default is INFO'
)
def main(idle_time, ignore_connections, log_level):
    logging.basicConfig(filename=log_fn,
                        format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)  # [s7]
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    logger.setLevel(level=numeric_level)
    logger.info('=' * 30)
    logger.info('AutoStop Script Starts ' + log_time())
    logger.debug(f'Parameters: idle_time {idle_time}, ignore_connections {ignore_connections}')

    idle = True

    data = get_jupyter_info()
    logger.info(f'Number of kernels: {len(data)}')        
    if len(data) > 0:
        if log_level.upper() == 'DEBUG':    
            logger.debug('Jupyter Kernels Info ' + log_time())
            for notebook in data:
                kernel_info = notebook.get('kernel')
                logger.debug((f"name: {notebook.get('path')}, "
                              f"state: {kernel_info.get('execution_state')}, "
                              f"conn: {kernel_info.get('connections')}, "
                              f"last: {str_to_datetime(kernel_info.get('last_activity')).isoformat(' ', 'seconds')}, "
                              f"idle_sec: {get_time_diff(kernel_info.get('last_activity'))}"))

        idle = is_idle(data, idle_time, ignore_connections)
        logger.info(f'Based on notebooks, is idle: {idle}')

    # Allow Sagemaker to warm up after just launching
    else:
        client = boto3.client('sagemaker')
        uptime = client.describe_notebook_instance(
            NotebookInstanceName=get_notebook_name()
        )['LastModifiedTime']  # sagemaker internal time is utc
        idle = (datetime.now(timezone.utc) - uptime).total_seconds() >= idle_time
        logger.info(f'Based on Sagemaker uptime, is idle: {idle}')
        # (datetime.now(timezone.utc) - datetime.fromtimestamp(psutil.boot_time(), timezone.utc))  # might be better for uptime?
            
    if idle:
        logger.info('Sagemaker is idle; therefore, is shutting down!')
        # client = boto3.client('sagemaker')
        # client.stop_notebook_instance(
        #     NotebookInstanceName=get_notebook_name()
        # )

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
















