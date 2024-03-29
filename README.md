Monitoring IPS Updates on CP Management Servers and managed Gateways
===========================================================================
![license](https://img.shields.io/github/license/leinadred/CP_IPS-Update-Monitoring4Nagios)	
![language](https://img.shields.io/github/languages/top/leinadred/CP_IPS-Update-Monitoring4Nagios)
Basic informations
---------------------

Script is logging into Checkpoint Management and checking the IPS Database Update Version and Installation Dates.

For the login, the SDK (<https://github.com/CheckPointSW/cp_mgmt_api_python_sdk>) is used (Option "unsafe=true" is passed to api, as Nagios is not able to respond to questions).

After successful logging in, we are parsing the API output from show-ip-status and comparing it with i.e actual date or "update available" followed by sending an API request to "show-simple-gateways" to fetch managed gateways and running "run-script -> "clish -c "show security-gateway ips status""" on them. Now the Versions of installed IPS are compared. if any of the checks above ends with a warning, state is "WARNING". if one check is in critical state, the script gives back "CRITICAL" state and so on. Only if all checks are "OK", an OK will be sent to nagios.
s based systems.

- OK = 0
- WARNING = 1
- CRITICAL = 2
- UNKNOWN = 3

(can be adjusted if needed - depending on use case)

The Thresholds for "WARNING" / "CRITICAL" are configurable within the script (on day base).

![OK - State](https://github.com/leinadred/CP_IPS-Update-Monitoring4Nagios/blob/master/ips_check_ok.png)
![WARNING - State](https://github.com/leinadred/CP_IPS-Update-Monitoring4Nagios/blob/master/ips_check_warn.png)

Installation
---------------------

Prerequisites:

- Python (worked for me with python 2.7, 3.6, 3.7, 3.8 and 3.9)
- Checkpoint Management API SDK (<https://github.com/CheckPointSW/cp_mgmt_api_python_sdk>)
- monitor.py (accessible and executable for executing user)
- user on Management Server to login via API (user and password, API Key based authentication might be implemented later)
- (the API user must have the right to execute "one time scripts" at gateways (user settings -> Permission Profile -> Gateways -> "Run One Time Script"))

My Environment - maybe it helps:

- Server - Centreon 20.04.5 on Centos 6
- installed python3.x
- installed Check Point Mgmt API SDK with *pip install git+<https://github.com/CheckPointSW/cp_mgmt_api_python_sdk>*
- installed used python modules, if they are not installed by default
- created a directory beneath "/usr/lib/centreon/plugins" called "added"
- "git clone <https://github.com/leinadred/CP_IPS-Update-Monitoring4Nagios/>"

Centreon specific configuration:

- created command for executing the script
- created a service template with all appropriate setting (either directly or via another template) and linked it with the command
- created a host and a service linked to that host, referencing to the service template, enter the Argument data here (Host, User, Password)

Deploy config

Issues / Bugs / Tips
----------------------

in case you have bugs, problems with using the script and so - please reach out  
I am kind of a beginner with python but will be happy to assist and/or learn more on python

Changelog
-------------

20200903

- added "-C" for Context, needed for SmartCloud-1

- added possibility to check IPS Version on managed gateways via the Management Server (Api Call "run-script")

20200906

- added optional arg "-M" for monitoring Management Servers IPS Version only and "-v" for verbosity and debugging

20201024

- added and improved error handling

  - when SMS did not get an IPS version update or was not able to fetch recent version
  - when SMS cannot reach a gateway
  - added more logging outputs at verbose executing (-v)

- for checking on "On Premise" SMS, use argument "-C none"

20201124

- Improved handling if gateways are not reached or IPS is disabled (will be mentioned in Output, but with state OK)

- corrected some typos

20210821

- Added -i and -s for ignore/select specific gateways

- smaller improvements 
