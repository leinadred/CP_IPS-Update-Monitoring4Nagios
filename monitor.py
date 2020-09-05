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
import sys, os
import datetime
import time
import argparse
import re
from cpapi import APIClient, APIClientArgs


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

output_code=[]
output_text={}
ipsver_mgmt=()

def fun_getipsver_mgmt():
    global output_text
    global output_code
    global ipsver_mgmt
    client_args = APIClientArgs(server=args.api_server, context=args.api_context, unsafe='True')
    with APIClient(client_args) as client:
        # If Errer occurs due to fingerprtnt mismatch
        if client.check_fingerprint() is False:
            output_text.update="Could not get the server's fingerprint - Check connectivity with the server."
            output_code.append("UNKNOWN")
        # login to server:
        login_res = client.login(args.api_user, args.api_pwd)
        # when login failed
        if login_res.success is False:
            output_text.update="Login failed: {}".format(login_res.error_message)
            output_code.append("UNKNOWN")
        else:
            #API Call "show ips status"
            res_ipsver_mgmt = client.api_call("show-ips-status")
            ipsver_mgmt=res_ipsver_mgmt.data["installed-version"]
    
    if ipsver_mgmt:
        #getting version numbers
        ips_current_ver_info=res_ipsver_mgmt.data["installed-version"]
        ips_update_ver_info=res_ipsver_mgmt.data["latest-version"]
        #bool update available - yes/no
        ips_bool_update=res_ipsver_mgmt.data["update-available"]
        #install dates
        ips_date_last_install=res_ipsver_mgmt.data["last-updated"]
        ips_date_last_install_iso=ips_date_last_install["iso-8601"]
        ips_date_last_install_posix=ips_date_last_install["posix"]
        #release date of last update
        ips_date_update=res_ipsver_mgmt.data["latest-version-creation-time"]
        #ips_date_update_iso=ips_date_update["iso-8601"]
        ips_date_update_posix=ips_date_update["posix"]
        #
        #
        ips_update_date_delta=datetime.datetime.fromtimestamp(ips_date_update_posix/1000) - datetime.datetime.fromtimestamp(ips_date_last_install_posix/1000)            
        #work with it
        if not ips_bool_update:
            output_text.update({"Monitor Management IPS Version": {"Result" : "OK! No Update available - Last installed update: "+ips_date_last_install_iso+" - Installed Version "+ips_current_ver_info+" - Newest: "+ips_update_ver_info}})
            output_code.append("OK")
            #raise SystemExit(OK)
        elif ips_update_date_delta.days > 3:
            output_text.update({"Monitor Management IPS Version": {"Result" : "CRITICAL! Updates available -  Last installed update: "+ips_date_last_install_iso+" - last Installed version"+ips_current_ver_info+"  - Newest: "+ips_update_ver_info+" - Update Date Delta: "+ips_update_date_delta.days+" Days!"}})
            output_code.append("CRITICAL")
            # raise SystemExit("CRITICAL")
        elif ips_update_date_delta.days > 0 and ips_update_date_delta.days < 0:
            output_text.update({"Monitor Management IPS Version": {"Result" : "WARNING! Updates available -  Last installed update: "+ips_date_last_install_iso+" - last Installed version"+ips_current_ver_info+"  - Newest: "+ips_update_ver_info+" - Update Date Delta: "+ips_update_date_delta.days+" Days!"}})
            output_code.append("WARNING")
        else:
            output_text.update({"Monitor Management IPS Version": {"Result" : "There is something wrong - please check! API Response: "+res_ipsver_mgmt.data}})
            output_code.append("UNKNOWN")
    else:
        output_text.update({"meh - something went wrong"})
        output_code.append("UNKNOWN")

    return output_text,output_code,ipsver_mgmt

def fun_getipsver_gws():
    global ipsver_mgmt
    global output_text
    global output_code
    #res_ipsver_mgmt=fun_getipsver_mgmt()
    #res_ipsver_mgmt["installed-version"]
    client_args = APIClientArgs(server=args.api_server, context=args.api_context, unsafe='True')
    with APIClient(client_args) as client:
        # If Errer occurs due to fingerprtnt mismatch
        if client.check_fingerprint() is False:
            output_text.update({"Monitor Logging into Mgmt API": {"Result": "Could not get the server's fingerprint - Check connectivity with the server."}})
            output_code.append("UNKNOWN")

        # login to server:
        login_res = client.login(args.api_user,args.api_pwd)

        # when login failed
        if login_res.success is False:
            output_text.update({"Monitor Logging into Mgmt API": {"Result": "Login failed: {}".format(login_res.error_message)}})
            output_code.append("UNKNOWN")
        res_getmanagedgws = client.api_call("show-simple-gateways",{"limit":"500"})
        gwselector=0
        totalgws=res_getmanagedgws.data['total']
        dict_ipsver_gw={}
        while gwselector < totalgws:
            gwname=res_getmanagedgws.data['objects'][gwselector]['name']
            res_ipsvermgmt_task = client.api_call("run-script",{"script-name":"get ips version","script":"clish -c \"show security-gateway ips status\"","targets" : gwname}) 
            ipsver_gw=re.search('IPS Update Version: (.+?), ', res_ipsvermgmt_task.data['tasks'][0]['task-details'][0]['statusDescription'])
            dict_ipsver_gw.update({ gwname: {"gwversion" : ipsver_gw.group(1),"mgmtversion" : ipsver_mgmt,"gwmgmtsame" : ipsver_mgmt==ipsver_gw.group(1)}})
            if ipsver_mgmt!=ipsver_gw.group(1):
                output_text.update({"Monitor Gateway "+gwname+" IPS Version": {"Result":"has not the same version as Management! "+ipsver_mgmt+" - Gw "+ipsver_gw.group(1)+""}})
                output_code.append("WARNING")
            elif ipsver_mgmt==ipsver_gw.group(1):
                output_text.update({"Monitor Gateway "+gwname+" IPS Version": {"Result":"OK! Mgmt "+ipsver_mgmt+" - Gw "+ipsver_gw.group(1)+""}})
                output_code.append("OK")
            else:
                output_text.update({"Monitor Gateway "+gwname+" IPS Version": {"Result":"UNKNOWN! Something weird happened"}})
                output_code.append("UNKNOWN")
            gwselector=gwselector+1
        #print(dict_ipsver_gw)
        #print(dict_ipsver_gw.items)
        #for item in dict_ipsver_gw:
        #    #if dict_ipsver_gw[item]!=ipsver_mgmt:
        #    if ipsver_mgmt!=ipsver_mgmt:
        #        output_text.update({"Monitor": "Gateway "+item+" IPS Version", "Result":"has not the same version as Management! "+ipsver_mgmt+" - Gw "+ipsver_gw.group(1)+""})
        #        output_code.append("WARNING")
        #    elif ipsver_mgmt==ipsver_mgmt:
        #        output_text.update({"Monitor": "Gateway "+item+" IPS Version", "Result":"OK! Mgmt "+ipsver_mgmt+" - Gw "+ipsver_gw.group(1)+""})
        #        output_code.append("OK")
    return output_text, output_code

def fun_nagiosize():
    #Primary built to centralize the "Unknown/OK/Error" Messages in one fplace, so the whole script is being run.
    #OK MESSAGE
    global output_text
    global output_code
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
        raise SystemExit("UNKNOWN! Something went wrong, please troubleshoot/debug script!")
    
if __name__ == "__main__":
    fun_getipsver_mgmt()
    fun_getipsver_gws()
    fun_nagiosize()

