#!/usr/bin/env python3
import argparse
import sys

#cgitb.enable()


#from JCMBSoftPyLib import HTML_Unit

from RemoteIt import RemoteIt

from pprint import pprint

import csv

import os

import requests
import json
from base64 import b64decode
import logging
import ipaddress
import re


try:
    from requests_http_signature import HTTPSignatureAuth
except:
    sys.exit("HTTPSignatureAuth is not installed. Install it using pip3 install requests_http_signature==v0.1.0")

import http.client as http_client
from requests_toolbelt.utils import dump


def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Account Summary.')

   parser.add_argument("key_id", help="Account Key",)
   parser.add_argument("key_secret_id", help="Account Secret ID",)
   parser.add_argument("to_account", help="email of account to transfer to",)
   parser.add_argument("Device_ID", help="Device ID", nargs="?")
   parser.add_argument("--Tell", help="Tell Settings",action="store_true")
   parser.add_argument("--DryRun", help="Do not delete, just show what would happen",action="store_true")
   parser.add_argument("--Verbose", help="Verbose",action="store_true")

   parser = parser.parse_args()
   args={}
   args["key_id"]=parser.key_id
   args["key_secret_id"]=parser.key_secret_id
   args["to_account"]=parser.to_account
   args["Device_ID"]=parser.Device_ID
   args["Verbose"]=parser.Verbose
#   args["HW_ID"]=args["HW_ID"].replace(":","")

   if parser.Tell :
      sys.stderr.write("key_id: {}\n".format(args["key_id"]))
      sys.stderr.write("key_secret_id: {}\n".format(args["key_secret_id"]))
      sys.stderr.write("to_account: {}\n".format(args["to_account"]))
      sys.stderr.write("Device_ID : {}\n".format(args['Device_ID']))
      sys.stderr.write("Verbose: {}\n".format(args['Verbose']))

   return (args)




def transferDevice(key_id,key_secret_id,to_account,Verbose, HW_ID):
    host = 'api.remote.it'
    url_path = '/graphql/v1'
    content_type_header = 'application/json'
    success=True
    message=None


    query = 'mutation { transfer ( deviceId: "' + HW_ID + '", email: "' + to_account + '" ) }'
#    print (query)


# Create the request payload
    body = {
        "query": query,
    }

#        print(body,file=sys.stderr)
    content_length_header = str(len(body))
    headers = {
        'host': host,
        'path': url_path,
        'content-type': content_type_header,
        'content-length': content_length_header,
    }

    response = requests.post('https://' + host + url_path,
                             json=body,
                             auth=HTTPSignatureAuth(algorithm="hmac-sha256",
                                                    key=b64decode(key_secret_id),
                                                    key_id=key_id,
                                                    headers=[
                                                        '(request-target)', 'host',
                                                        'date', 'content-type',
                                                        'content-length'
                                                    ]),
                             headers=headers)
    data = dump.dump_all(response)
#        print(data.decode('utf-8'))
    if response.status_code != 200:
        sys.stderr.write("Error in Request\n")
        sys.stderr.write(response.text)
        success=False

    reply=response.json()
#    pprint(reply)


    if "errors" in reply:
        if Verbose:
    #        pprint(reply,stream=sys.stderr)
            message=reply["errors"][0]["message"]
            print("Error: {}".format(message))


#        sys.stderr.write(reply)
        success=False
    else:
        print("Device with HW_ID {} Transferred to {}\n".format(HW_ID,to_account))


    return(success)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


def main():
   args=get_args()
#   pprint(args)

   if not is_valid_email(args["to_account"]) :
      sys.exit("eMail address {} is invalid".format(args["to_account"]))


   if args["Device_ID"] == None:
      sys.exit("HW Must be provided when deleting a single value")


   if os.path.isfile(args["Device_ID"]):
      if args["Verbose"]:
         sys.stdout.write ("Using CSV file: {}\n".format(args["Device_ID"]))

      with open(args["Device_ID"], 'r') as file:
         reader = csv.reader(file)
         header=next(reader)
#         print(header)
         if header != ['id', 'name', 'hardwareId', 'title', 'state', 'timestamp', 'created', 'address']:
            sys.exit("CSV file not of the correct format. Should have fields 'id', 'name', 'hardwareId', 'title', 'state', 'timestamp', 'created', 'address'")

         for row in reader:
            if transferDevice(args["key_id"],args["key_secret_id"],args["to_account"], args["Verbose"],row[0]):
                print("Success: {} with Device_ID {} Transfered to {} ".format(row[1],row[0],args["to_account"]))
            else:
                print("Error:   {} with Device_ID {} Mot Transfered to {} ".format(row[1],row[0],args["to_account"]))

   else:
       if transferDevice(args["key_id"],args["key_secret_id"],args["to_account"],args["Verbose"],args["Device_ID"]):
           print("Success: {} Transfered to {} ".format(args["Device_ID"],args["to_account"]))
       else:
           print("Error:   {} Mot Transfered to {} ".format(args["Device_ID"],args["to_account"]))


#   pprint(remotes)

if __name__ == '__main__':
    main()
