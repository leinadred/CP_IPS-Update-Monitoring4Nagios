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
# Edit Sept 2020
# Now all managed Gateways are been checked (API CALL - Run Script - show security-gateway ips status, then fetching version and comparing)
# reworked into functions - Feedback is given by extra function and will give back all Results!

from __future__ import print_function
import getpass
import sys, os, logging
import datetime
import time
import argparse
import re
from cpapi import APIClient, APIClientArgs


#################################################################################################
# set args                                                                                      #
#################################################################################################
parser = argparse.ArgumentParser()
parser.add_argument('-H', '--api_server', help='Target Host (CP Management Server)')
parser.add_argument('-U', '--api_user', help='API User')
parser.add_argument('-P', '--api_pwd', help='API Users Password')
parser.add_argument('-C', '--api_context', help='If SmartCloud-1 is used, enter context information here (i.e. bhkjnkm-knjhbas-d32424b/web_api) - for On Prem enter \"-C none\"')
parser.add_argument('-M', '--mgmtonly', help="check IPS version on Management Station only", action="store_true")
parser.add_argument('-v', '--verbose', help='Run Script with logging output - Troubleshooting and so', action='store_true')
args = parser.parse_args()


if args.api_context == "none":
    args.api_context = False
#################################################################################################
# CONSTANTS FOR RETURN CODES UNDERSTOOD BY NAGIOS                                               #                                                              #
#################################################################################################
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

output_code=[]
output_text={}
ipsver_mgmt=()

#################################################################################################
# ADDING DEBUG MODE                                                                             #                                                              #
#################################################################################################
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

logging.debug("################## Starting - With extended Logging ##################")

def fun_getipsver_mgmt():
    global output_text
    global output_code
    global ipsver_mgmt
    if args.api_context:
        client_args = APIClientArgs(server=args.api_server, context=args.api_context, unsafe='True')
    else:
        client_args = APIClientArgs(server=args.api_server, unsafe='True')
    with APIClient(client_args) as client:
        # If Error occurs due to fingerprint mismatch
        if client.check_fingerprint() is False:
            output_text.update({"Message":"Could not get the server's fingerprint - Check connectivity with the server."})
            output_code.append("UNKNOWN")
            print("UNKNOWN! Logging into SMS not successful! Please troubleshoot/debug script! "+str(output_text))
            raise SystemExit(UNKNOWN)
        # login to server:
        login_res = client.login(args.api_user, args.api_pwd)
        logging.debug('API Login done: '+str(login_res))
        # when login failed
        if not login_res.success:
            output_text.update({"Message":"Login failed: "+str(login_res.error_message)})
            output_code.append("UNKNOWN")
            print("UNKNOWN! Logging into SMS not successful! Please troubleshoot/debug script! "+str(output_text))
            raise SystemExit(UNKNOWN)
        else:
            #API Call "show ips status"
            res_ipsver_mgmt = client.api_call("show-ips-status")
            ipsver_mgmt=res_ipsver_mgmt.data["installed-version"]
    if ipsver_mgmt:
        logging.debug('API Output:' +str(res_ipsver_mgmt))
        #getting version numbers
        ips_current_ver_info=res_ipsver_mgmt.data["installed-version"]
        ips_update_ver_info=res_ipsver_mgmt.data["latest-version"]
        #bool update available - yes/no
        ips_bool_update=res_ipsver_mgmt.data["update-available"]
        #install dates
        ips_date_last_install=res_ipsver_mgmt.data["last-updated"]
        ips_date_last_install_iso=ips_date_last_install["iso-8601"]
        ips_date_last_install_posix=ips_date_last_install["posix"]
        if "N/A" not in res_ipsver_mgmt.data["latest-version"]:
            ips_date_update=res_ipsver_mgmt.data["latest-version-creation-time"]
            ips_date_update_posix=ips_date_update["posix"]
        else:
            pass
        #
        #
        if "N/A" not in res_ipsver_mgmt.data["latest-version"]:
            ips_update_date_delta=((ips_date_last_install_posix/1000 - ips_date_update_posix/1000))/(60*60*24)
            logging.debug('Fetched Management IPS Version: '+str(ips_current_ver_info)+", most recent:"+str(ips_current_ver_info)+" From:"+str(ips_date_last_install_iso))
            #work with it
            if not ips_bool_update:
                logging.debug("Update available: " +str(ips_bool_update))
                output_text.update({"Monitor Management IPS Version": {"Result" : "OK! No Update available - Last installed update: "+str(ips_date_last_install_iso)+" - Installed Version "+str(ips_current_ver_info)+" - Newest: "+str(ips_update_ver_info)}})
                output_code.append("OK")
            elif ips_update_date_delta > 3:
                logging.debug("Update available: " +str(ips_bool_update))
                output_text.update({"Monitor Management IPS Version": {"Result" : "CRITICAL! Updates available -  Last installed update: "+str(ips_date_last_install_iso)+" - last Installed version "+str(ips_current_ver_info)+"  - Newest: "+str(ips_update_ver_info)+" - Update Date Delta: "+str(ips_update_date_delta)+" Days!"}})
                output_code.append("CRITICAL")
            elif ips_update_date_delta > 0 and ips_update_date_delta < 3:
                logging.debug("Update available: " +str(ips_bool_update))
                output_text.update({"Monitor Management IPS Version": {"Result" : "WARNING! Updates available -  Last installed update: "+str(ips_date_last_install_iso)+" - last Installed version "+str(ips_current_ver_info)+"  - Newest: "+str(ips_update_ver_info)+" - Update Date Delta: "+str(ips_update_date_delta)+" Days!"}})
                output_code.append("WARNING")
            else:
                logging.debug("Something is wrong - API Response: " +str(login_res))
                output_text.update({"Monitor Management IPS Version": {"Result" : "There is something wrong - please check! API Response (with -v)"}})
                output_code.append("UNKNOWN")
        elif "N/A" in res_ipsver_mgmt.data["latest-version"]:
            logging.debug("No or invalid value for \"latest-version\" - was there ever an IPS update been downloaded?" +str(login_res))
            output_text.update({"Monitor Management IPS Version": {"Result" : "No or invalid value for \"latest-version\" - was there ever an IPS update been downloaded?"}})
            output_code.append("CRITICAL")        

    else:
        logging.debug("Something is wrong - API Response: " +str(login_res))
        output_text.update({"Message":"meh - something went wrong"})
        output_code.append("UNKNOWN")
        sys.exit("LogIn failed! API Response: "+str(login_res))

    return output_text,output_code,ipsver_mgmt

def fun_getipsver_gws():
    global ipsver_mgmt
    global output_text
    global output_code
    if args.api_context:
        client_args = APIClientArgs(server=args.api_server, context=args.api_context, unsafe='True')
    else:
        client_args = APIClientArgs(server=args.api_server, unsafe='True')
    with APIClient(client_args) as client:
        # If Error occurs due to fingerprint mismatch
        if client.check_fingerprint() is False:
            output_text.update({"Monitor Logging into Mgmt API": {"Result": "Could not get the server's fingerprint - Check connectivity with the server."}})
            output_code.append("UNKNOWN")
            print("UNKNOWN! Logging into SMS not successful! Please troubleshoot/debug script! "+str(output_text))
            raise SystemExit(UNKNOWN)
        # login to server:r
        login_res = client.login(args.api_user,args.api_pwd)

        # when login failed
        if login_res.success is False:
            logging.debug("Something is wrong - API Response: " +str(login_res))
            output_text.update({"Monitor Logging into Mgmt API": {"Result": "Login failed: {}".format(login_res.error_message)}})
            output_code.append("UNKNOWN")
            print("UNKNOWN! Logging into SMS not successful! Please troubleshoot/debug script! "+str(output_text))
            raise SystemExit(UNKNOWN)
        res_getmanagedgws = client.api_call("show-simple-gateways",{"limit":"500"})
        gwselector=0
        totalgws=res_getmanagedgws.data['total']
        logging.debug("Checking IPS version on "+str(res_getmanagedgws.data['total'])+" Gateways")
        dict_ipsver_gw={}
        while gwselector <= totalgws-1:
            gwname=res_getmanagedgws.data['objects'][gwselector]['name']
            res_ipsvergw_task = client.api_call("run-script",{"script-name":"get ips version","script":"clish -c \"show security-gateway ips status\"","targets" : gwname}) 
            if res_ipsvergw_task.success is True:               
                res_ipsvergw_task_result=client.api_call("show-task",{"task-id" : res_ipsvergw_task.data['tasks'][0]['task-id'],"details-level":"full"}).data['tasks'][0]['task-details'][0]['statusDescription']
                if res_ipsvergw_task_result!="IPS Blade is disabled":
                    ipsver_gw=re.search('IPS Update Version: (.+?), ', res_ipsvergw_task_result)
                    dict_ipsver_gw.update({ gwname: {"gwversion" : ipsver_gw.group(1),"mgmtversion" : ipsver_mgmt,"gwmgmtsame" : ipsver_mgmt==ipsver_gw.group(1)}})
                    if ipsver_mgmt!=ipsver_gw.group(1):
                        output_text.update({"Monitor Gateway "+str(gwname)+" IPS Version": {"Result":"has not the same version as Management! Management:"+str(ipsver_mgmt)+" - Gw:"+str(ipsver_gw.group(1))+""}})
                        output_code.append("WARNING")
                    elif ipsver_mgmt==ipsver_gw.group(1):
                        output_text.update({"Monitor Gateway "+str(gwname)+" IPS Version": {"Result":"OK! Mgmt "+str(ipsver_mgmt)+" - Gw "+str(ipsver_gw.group(1))+""}})
                        output_code.append("OK")
                    else:
                        output_text.update({"Monitor Gateway "+str(gwname)+" IPS Version": {"Result":"UNKNOWN! Something weird happened"}})
                        output_code.append("UNKNOWN")
                    logging.debug("IPS version on "+str(gwname)+": "+ipsver_gw.group(1))
                else:
                    output_text.update({"Monitor Gateway "+str(gwname)+" IPS Version":{"Result":"IPS Blade disabled - Ignoring"}})
                    output_code.append("OK")
            else:
                output_text.update({"Monitor Gateway "+str(gwname)+" IPS Version": {"Result":"Error - Gateway check failed! Check Connection!"}})
                output_code.append("WARNING")
                logging.debug("Gateway check failed on "+str(gwname)+"! Check Connection!")
            gwselector=gwselector+1
    return output_text, output_code

def fun_nagiosize():
    #Primary built to centralize the "Unknown/OK/Error" Messages in one place, so the whole script is being run.
    global output_text
    global output_code
    logging.debug("Work is done - create and give feedback to Monitoring Engine: "+str(output_code)+" Message: "+str(output_text))
    if "CRITICAL" in output_code:
        print("CRITICAL! "+str(output_text))
        raise SystemExit(CRITICAL)
    elif "WARNING" in output_code:
        print("WARNING! "+str(output_text))
        raise SystemExit(WARNING)
    elif "UNKNOWN" in output_code:
        print("UNKNOWN! "+str(output_text))
        raise SystemExit(UNKNOWN)
    elif all(ele == "OK" for ele in output_code):
        print("OK! "+str(output_text))
        raise SystemExit(OK)
    else:
        print("UNKNOWN! Something went wrong, please troubleshoot/debug script! "+str(output_text))
        raise SystemExit(UNKNOWN)

if __name__ == "__main__":
    if args.mgmtonly:
        fun_getipsver_mgmt()
        fun_nagiosize()
    else:
        fun_getipsver_mgmt()
        fun_getipsver_gws()
        fun_nagiosize()
