#!/bin/bash

conda install click -y

# Tells bash that it should exit the script if any statement
# returns a non-true return value. This prevent errors snowballing
# into serious issues when they could have been caught earlier. 
set -o errexit

# Overview
# IDLE_TIME = how long to idle before shutdown (1 hour default)
# --ignore-connections = Shutdown even though a user is connected with the notebooks
# Ensure the Notebook Instance execution role permissions to SageMaker:StopNotebookInstance 
#   to stop the notebook and SageMaker:DescribeNotebookInstance to describe the notebook.

# PARAMETERS
IDLE_TIME=3600
# new parameters for how often to check

echo "Starting the SageMaker autostop script in cron"

# TODO: Need to understand this line of code
# TODO: Have many different permutation as tutorial on how to use.
# TOOD: Have tutorial on cron like what each position of the scheduler and what to change for desire results
# (crontab -l 2>/dev/null; echo "5 * * * * /home/ec2-user/anaconda3/envs/JupyterSystemEnv/bin/python3.6 $PWD/autostop.py --idle-time $IDLE_TIME --ignore-connections") | crontab -
# (crontab -l 2>/dev/null; echo "* * * * * /home/ec2-user/anaconda3/envs/JupyterSystemEnv/bin/python $PWD/autostop.py --idle-time $IDLE_TIME") | crontab -
# echo "* * * * * /home/ec2-user/anaconda3/envs/JupyterSystemEnv/bin/python3.6 $PWD/autostop.py --idle-time 60" | crontab -

# echo "@hourly /home/ec2-user/anaconda3/envs/JupyterSystemEnv/bin/python $PWD/autostop.py --idle-time $IDLE_TIME --log-dir $PWD" | crontab -
# echo "0 2-17 * * * /home/ec2-user/anaconda3/envs/JupyterSystemEnv/bin/python $PWD/autostop.py --idle-time $IDLE_TIME --log-dir $PWD" | crontab -

# cat /var/log/cron  # to see things that cron ran like your own script. 
# crontab -l  # to see what cron job is running
# crontab -r  # to remove all uer cron jobs
# crontab -e  # to edit the schedule of a cron job