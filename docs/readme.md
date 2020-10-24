# CP_IPS-Update-Monitoring4Nagios
Script is logging into Checkpoint Management and checking the IPS Database Update Version and Installation Dates.

For the login, the SDK (https://github.com/CheckPointSW/cp_mgmt_api_python_sdk) is used (Option "unsafe=true" is passed to api, as Nagios is not able to respond to questions).

After successful logging in, we are parsing the API output from show-ip-status and comparing it with i.e actual date or "update available" followed by sending an API request to "show-simple-gateways" to fetch managed gateways and running "run-script -> "clish -c "show security-gateway ips status""" on them. Now the Versions of installed IPS are compared. if any of the checks above ends with a warning, state is "WARNING". if one check is in critical state, the script gives back "CRITICAL" state and so on. Only if all checks are "OK", an OK will be sent to nagios. 
s based systems.

OK = 0 - WARNING = 1 - CRITICAL = 2 - UNKNOWN = 3
![alt text](https://github.com/leinadred/CP_IPS-Update-Monitoring4Nagios/blob/master/ips_check_ok.png?raw=true)
![alt text](https://github.com/leinadred/CP_IPS-Update-Monitoring4Nagios/blob/master/ips_check_warn.png?raw=true)

The Thresholds for "WARNING" / "CRITICAL" are configurable within the script (on daily base).

To use it on Nagios Server you need:
python installed (script worked with 2.7, 3.6 and 3.7)

how this is installed on my machine (CENTREON 20.04.5): 
  in /usr/lib/centreon/plugins added a folder "added" with scipts not coming from centreon (in case centreon is updating their plugins, they won´t delete my :)
  installed python3.x (CentOS delivers 3.6, which works)
  installed Checkpoint SDK (link above) with *pip install git+https://github.com/CheckPointSW/cp_mgmt_api_python_sdk*  
  *chmod +x monitor.py* - otherwise execute the file like *python(2/3/3.x) monitor.py -H HOSTADDRESS [-C context-lik-12389123-1231/web_api ] -U apiuser -P securepass*
  changed owner and group of monitor.py to centreon-engine (will differ depending on solution you are using, might also be "nagios")
  create command and checks at monitoring engine level. 
  

