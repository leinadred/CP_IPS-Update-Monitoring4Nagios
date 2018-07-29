# CP_IPS-Update-Monitoring4Nagios
Script is logging into Checkpoint Management and checking the IPS Database Update Version and Installation Dates.

For the login, the SDK (https://github.com/CheckPointSW/cp_mgmt_api_python_sdk) is used (i changed one option in Login part of mgmt_api.py: (unsafe_auto_accept --> true) should work with the default - false - too, but was easier for me.

After successful logging in, we are parsing the API output from show-ip-status and comparing it with i.e actual date or "update available".

After some calculating and comparing the script gives output, understandable for Nagios based systems.

UNKNOWN = -1 - OK = 0 - WARNING = 1 - CRITICAL = 2


The Thresholds are freely configurable (on daily base).



To use it on Nagios Server you need:

python installed (script worked with 2.7 and 3.7

in the plugin folder i created an own "checkpoint" folder, containing the SDK and my script.

