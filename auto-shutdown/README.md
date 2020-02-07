# Auto-Shutdown 

Scripts to automatically shutdown server once jupyter is idling. 

# Files

`start-cron.sh`

> Script for starting a cron job that leverages the autostop.py script. 

`autostop.py`

> A script that deteremines whether the server is idling and shut the SageMaker down. 

`within_notebook_shutdown.ipynb`

> A collection of code for shutdowing the server once a notebook is finish running. 

`test_autostop.py`

> For future, unit testing. 

# Notes

* Bug? If you happen to close all your notebook during the cron job, it will initiate shutdown because uptime has been reached and there are no notebook therefore it is idle. This is a rare edge case so it isn't that big of a problem unless the cron schedule is very frequent. 
* Connections to notebook can be buggy meaning there would be more connection than expected. 


# Future

- [ ] add unittest 
- [ ] add some psutil stats like cpu, gpu, uptime, etc. This is useful when people are using terminal instead of notebooks to run scripts. 
- [ ] ability to record stats for a period of time an average them
- [ ] figure out a better way for uptime when the Sagemaker just launch. Should the script only run after 1 hour of up time?
- [ ] Add override for office hours? and maybe work days?

