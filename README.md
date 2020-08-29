# CP_IPS-Update-Monitoring4Nagios
Script is logging into Checkpoint Management and checking the IPS Database Update Version and Installation Dates.

For the login, the SDK (https://github.com/CheckPointSW/cp_mgmt_api_python_sdk) is used (Option "unsafe=true" is passed to api, as Nagios is not able to respond to qustions).

After successful logging in, we are parsing the API output from show-ip-status and comparing it with i.e actual date or "update available".

After some calculating and comparing the script gives output, understandable for Nagios based systems.

OK = 0 - WARNING = 1 - CRITICAL = 2 - UNKNOWN = 3


The Thresholds are freely configurable (on daily base).

To use it on Nagios Server you need:
python installed (script worked with 2.7, 3.6 and 3.7)

how this is installed on my machine (CENTREON 20.04.5): 
  in /usr/lib/centreon/plugins added a folder "added" with scipts not coming from centreon (in case centreon is updatin their plugins, they won´t delete my :)
  installed python3.x (CentOS delivers 3.6, which works)
  installed Checkpoint SDK (link above) with pip install git+https://github.com/CheckPointSW/cp_mgmt_api_python_sdk
  changed owner and group of monitor.py to centreon-engine (will differ depending on solution you are using)

configured Command, Service Templates and Services on CENTREON WebUI

Done
