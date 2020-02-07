#!/bin/bash

# the only package that is missing from JupyterSystemEnv
conda install click -y

# Tells bash that it should exit the script if any statement
# returns a non-true return value. This prevent errors snowballing
# into serious issues when they could have been caught earlier. [s2]
set -o errexit

# Overview
# IDLE_TIME = how often to run script and how long to idle before shutdown (1 hour default)
# LOG_DIR = where should the log file for this script be saved. Default is root folder. 
# --ignore-connections = Shutdown even though a user is connected with the notebooks
# Ensure the Notebook Instance execution role permissions to SageMaker:StopNotebookInstance 
#   to stop the notebook and SageMaker:DescribeNotebookInstance to describe the notebook.

# PARAMETERS
IDLE_TIME=3600
LOG_DIR=$PWD

echo "Starting the SageMaker autostop script in cron"

# Sample cron command
# Check for idle status every 5 minutes and save log file at present working directory
echo "*/5 * * * * /home/ec2-user/anaconda3/envs/JupyterSystemEnv/bin/python3.6 $PWD/autostop.py --idle-time $IDLE_TIME --log-dir $LOG_DIR" | crontab -

# Check for idle status every min
# echo "* * * * * /home/ec2-user/anaconda3/envs/JupyterSystemEnv/bin/python3.6 $PWD/autostop.py --idle-time $IDLE_TIME --log-dir $LOG_DIR" | crontab -

# Check for idle status at the start of the hour only during the hours from 2-17 which is PST non-business hours (6pm - 7am)
# echo "0 2-17 * * * /home/ec2-user/anaconda3/envs/JupyterSystemEnv/bin/python3.6 $PWD/autostop.py --idle-time $IDLE_TIME --log-dir $LOG_DIR" | crontab -

# Check for idle status every min while ignoring the fact that someone's browser is still accessing the notebooks
# echo "* * * * * /home/ec2-user/anaconda3/envs/JupyterSystemEnv/bin/python3.6 $PWD/autostop.py --idle-time $IDLE_TIME --log-dir $LOG_DIR --ignore-connections" | crontab -

# Notes
# Tutorial on Cron [s1]
# ┌-------- min (0 - 59)
# | ┌--------- hour (0 - 23)
# | | ┌----------- day of month (1 - 31)
# | | | ┌------------- month (1 - 12)
# | | | | ┌--------------- day of week (0 - 6 are sun to sat, or use names; 7 is also Sunday)
# | | | | |
# | | | | |
# * * * * *
# cat /var/log/cron  # to see what scripts in general was ran by cron.  
# crontab -l  # to see what cron job is running for current user
# crontab -r  # to remove all user cron jobs
# crontab -e  # to edit the schedule of a cron job

# print out cron schedule
crontab -l 

# WARNING: This script does't not take into account scripts that are ran in a terminal. Everything must be done in a jupyter notebook. 
# WARNING: Sometime SageMaker will have 1+ connection on a notebook even though there is 1 or 0 users using that notebook. So ignore-connections might be useful
# If you get a syntax error when you use cron runs the python script but not when you run it manually. It is because it is using the wrong python version.
# To run script manually. > python autostop.py --idle-time 60
# Good idea to cd into the same location as where the python script is at. 
# Best to set the log file in SageMaker dir or sub-dir so that you have a record after shutdown. 
# The log file is great to see the status output for debugging and for telling when the Sagemaker instance was shutdown automatically.
# If there is an error with cron, it will be saved in /var/spool/mail/ec2-user.
# To throw away errors. > (crontab -l 2>/dev/null; echo "[cron commands]") | crontab -
# Sagemaker is in UTC timezone so you can use [s3] for your local time.
# An alternative is to run the shutdown command in your jupyter notebook after your script. Please refer to within_notebook_shutdown.ipynb

# Source
# [s1] https://www.ostechnix.com/a-beginners-guide-to-cron-jobs/ 
# [s2] https://pubs.opengroup.org/onlinepubs/9699919799.2018edition/utilities/V3_chap02.html#set
# [s3] https://www.worldtimebuddy.com/

