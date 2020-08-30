#!/usr/bin/python3
#
# monitor.py
# version 1.0
#
# written by Daniel Meier (github.com/leinadred)
# July 2018 - updated references to recent cpapi June 2019
# Edit Aug 2020 
# updated references 
# added "context" as argument to check for Smart1 Cloud instances
# corrected States/Exit Codes(Unknown" is "3" now)
# added to "client_args" - unsafe=True - for not having to handle fingerprints and certificates, as monitoring is not done manually ("do you accept fingerprint xyz?")
# 

from __future__ import print_function
# A package for reading passwords without displaying them on the console.
import getpass
import sys, os
import datetime
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--api_server', help='Target Host (CP Management Server)')
parser.add_argument('-U', '--api_user', help='API User')
parser.add_argument('-P', '--api_pwd', help='API Users Password')
parser.add_argument('-C', '--api_context', help='If SmartCloud-1 is used, enter context information here (i.e. bhkjnkm-knjhbas-d32424b/web_api)')
args = parser.parse_args()

# CONSTANTS FOR RETURN CODES UNDERSTOOD BY NAGIOS
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# IMPORT Checkpoint SDK
from cpapi import APIClient, APIClientArgs


def main():
    client_args = APIClientArgs(server=args.api_server, context=args.api_context, unsafe='True')
    with APIClient(client_args) as client:
        # If Errer occurs due to fingerprtnt mismatch
        if client.check_fingerprint() is False:
            print("Could not get the server's fingerprint - Check connectivity with the server.")
            raise SystemExit("UNKNOWN")

        # login to server:
        login_res = client.login(args.api_user, args.api_pwd)

        # when login failed
        if login_res.success is False:
            print("Login failed: {}".format(login_res.error_message))
            raise SystemExit("UNKNOWN")
        
        #API Call "show ips status"
        monitor_ips_version = client.api_call("show-ips-status")
        if monitor_ips_version.success:
            #fetching data from response
            ips_info=monitor_ips_version.data
            #getting version numbers
            ips_current_ver_info=ips_info["installed-version"]
            ips_update_ver_info=ips_info["latest-version"]
            #bool update available - yes/no
            ips_bool_update=ips_info["update-available"]
            #install dates
            ips_date_last_install=ips_info["last-updated"]
            ips_date_last_install_iso=ips_date_last_install["iso-8601"]
            ips_date_last_install_posix=ips_date_last_install["posix"]
            #release date of last update
            ips_date_update=ips_info["latest-version-creation-time"]
            #ips_date_update_iso=ips_date_update["iso-8601"]
            ips_date_update_posix=ips_date_update["posix"]
            #
            #
            ips_update_date_delta=datetime.datetime.fromtimestamp(ips_date_update_posix/1000) - datetime.datetime.fromtimestamp(ips_date_last_install_posix/1000)            
            #work with it
            if not ips_bool_update:
                print("OK! No Update available - Last installed update: {0} - Installed Version {1}" .format(ips_date_last_install_iso, ips_current_ver_info))
                raise SystemExit(OK)
            elif ips_update_date_delta.days > 3:
                print("CRITICAL! Updates available -  Last installed update: {0} - last Installed {1}; available {2} - Update Date Delta: {3} Days!" .format(ips_date_last_install_iso, ips_current_ver_info, ips_update_ver_info,ips_update_date_delta.days))
                raise SystemExit("CRITICAL")
            elif ips_update_date_delta.days > 0 and ips_update_date_delta.days < 0:
                print("WARNING! Updates available -  Last installed update: {0} - last Installed {1}; available {2} - Update Date Delta: {3} Days" .format(ips_date_last_install_iso, ips_current_ver_info, ips_update_ver_info,ips_update_date_delta.days))
                raise SystemExit("WARNING")
            else:
                print("There is something wrong - please check! API Response:", ips_info)
                raise SystemExit("UNKNOWN")
        else:
            print("meh - something went wrong")
            raise SystemExit("UNKNOWN")

if __name__ == "__main__":
    main()
