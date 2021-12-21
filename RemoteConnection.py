#!/usr/bin/env python3
import requests
import json
import os
from pprint import pprint
import argparse
import sys
from datetime import datetime
import urllib.parse

import cgitb
cgitb.enable()

from JCMBSoftPyLib import HTML_Unit


try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
#http_client.HTTPConnection.debuglevel = 1


base_url = "https://api.remot3.it/apv/v27/"


def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Account Summary.')
   parser.add_argument("username", help="Account User name",)
   parser.add_argument("password", help="Account password",)
   parser.add_argument("key", help="Account developer key",)
   parser.add_argument("device_address", help="Service ID",)
   parser.add_argument("connection_type", help="Type of the connection")
   parser.add_argument("--IP", help="IP Address of client that will connected to the service",default="0.0.0.0")

   parser = parser.parse_args()
   args={}
   args["username"]=parser.username
   args["password"]=parser.password
   args["dev_key"]=parser.key
   args["device_address"]=parser.device_address
   args["connection_type"]=parser.connection_type
   args["IP"]=parser.IP

#   print (args["username"])
#   print (args["password"])
#   print (args["dev_key"])

#   if args["username"] == None or args["password"] == None or args["dev_key"]:
#  Did not get one of the values, Get them from the config file

   return (args)


def connect_to_remote_it(username,password,dev_key):
   headers = {
       "developerkey": dev_key
   }
   body = {
       "password": password,
       "username": username
   }
   url = base_url +"user/login"


   response = requests.post(url, data=json.dumps(body), headers=headers)
   response_body = response.json()
#   pprint (response_body)

   token=response_body["token"]
   return(token)

#https://api.remot3.it/apv/v27/device/count/
#https://api.remot3.it/apv/v27/
#{"devicestate":"all","devicename":"SNM941"}

def get_devices_by_name(dev_key,token,model):
#print("Status Code: %s" % response.status_code)
#print("Raw Response: %s" % response.raw)
#print("Token: %s" % token)

   headers = {
      "developerkey": dev_key,
      "token": token,
      "Content-Type": "application/json"

   }


#   pprint(headers)

   url = base_url + "device/find/by/name/"
#   print (model)
#   print (url)
#   print (headers)
#   print ({"devicestate":"all","devicename":model})

   response = requests.post(url, headers=headers, json={"devicestate":"all","devicename":model})
#   print("Status Code: %s" % response.status_code)
   return (response.json())


def get_device_URL(dev_key,token,device_address,remote_ip):
#print("Status Code: %s" % response.status_code)
#print("Raw Response: %s" % response.raw)
#print("Token: %s" % token)

   headers = {
      "developerkey": dev_key,
      "token": token
   }

#   pprint(headers)

   url = base_url + "device/connect"
#   print (model)
#   print (url)
#   print (headers)
#   print ({"devicestate":"all","devicename":model})

   response = requests.post(url, headers=headers, json={"deviceaddress":device_address,"wait":"true","hostip":remote_ip})
#   print("Status Code: %s" % response.status_code)
   return (response.json())




def main():
   HTML_File=sys.stdout;
   HTML_Unit.output_html_header(HTML_File,"Remote Connection")
   HTML_Unit.output_html_body(HTML_File)
   args=get_args()
    
#  pprint(args)
   token=connect_to_remote_it(args["username"],args["password"],args["dev_key"])
   #print(token)
   connect_details=get_device_URL(args["dev_key"],token,args["device_address"],args["IP"])
   if connect_details["status"] == "true":
       if args["connection_type"]=="Basic%20Web":
          print ('<a href="http://{0}:{1}/">http://{0}:{1}</a>'.format(connect_details["connection"]["proxyserver"],connect_details["connection"]["proxyport"]))
       elif args["connection_type"]=="SSH":
          print ('<a href="ssh://root@{0}:{1}/">ssh://root@{0}:{1}</a>'.format(connect_details["connection"]["proxyserver"],connect_details["connection"]["proxyport"]))
       elif args["connection_type"]=="VNC":
          print ('<a href="vnc://{0}:{1}/">vnc://{0}:{1}</a>'.format(connect_details["connection"]["proxyserver"],connect_details["connection"]["proxyport"]))
       else:    
          print ('URL <a href="http://{0}:{1}/">http://{0}:{1}</a>'.format(connect_details["connection"]["proxyserver"],connect_details["connection"]["proxyport"]))
   else:
       print (connect_details["code"],connect_details["reason"])
#   pprint (connect_details)
   HTML_File.write("<h2>Access is from ip {} only<h/h2>".format(args["IP"]))
   HTML_Unit.output_html_footer(HTML_File,[])
   
if __name__ == '__main__':
    main()
