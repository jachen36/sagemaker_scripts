import boto3
import click
from datetime import datetime
import json
from notebook import notebookapp
import requests

def get_time_diff(last_activity):
    """Return the time differences in seconds"""
    last_activity = datetime.strptime(last_activity,"%Y-%m-%dT%H:%M:%S.%fz")
    return (datetime.utcnow() - last_activity).total_seconds()

def get_notebook_name():
    """Get Sagemaker ID"""
    log_path = '/opt/ml/metadata/resource-metadata.json'
    with open(log_path, 'r') as logs:
        _logs = json.load(logs)
    return _logs['ResourceName']

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

def get_jupyter_info():
    """Return a list of active notebooks in jupyter server"""
    # assume there are only 1 jupyter session on server
    server_info = list(notebookapp.list_running_servers())[0]  # [s1] get server info
    headers = {'Authorization': 'token ' + server_info['token'], 
               'Connection':'close'}  # [s3] to be safe
    response = requests.get(server_info['url'] + 'api/sessions',  # [s4] sessions has more info than api/kernels
                            headers=headers, 
                            verify=False)  # [s5] do not verify ssl ceritificates
    return response.json()  # return a list of active notebooks if any

@click.command()
@click.option(
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
def main(port, idle_time, ignore_connections):
    print("I'm a beautiful CLI")
    if len(data) > 0:
    idle = is_idle(data)

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
















