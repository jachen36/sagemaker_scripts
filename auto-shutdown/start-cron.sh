#!/bin/bash

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
# (crontab -l 2>/dev/null; echo "5 * * * * /usr/bin/python $PWD/autostop.py --idle-time $IDLE_TIME --ignore-connections") | crontab -
