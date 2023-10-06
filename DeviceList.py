#!/usr/bin/env python3
import os
import requests
import json
from base64 import b64decode
from pprint import pprint
import sys
import logging
import argparse
import ipaddress
import time
from enum import Enum



try:
   from requests_http_signature import HTTPSignatureAuth
#    from requests_http_signature import HTTPSignatureAuth, algorithms
except:
    sys.exit("HTTPSignatureAuth is not installed. Install it using pip3 install requests-http-signature==0.2.0")

import http.client as http_client

HW_ID=0
ID=1
INTERNAL_ID=2
TYPE=3
ACTIVE=4
LAST_CONTACT=5
CREATED=6




def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Account Summary.')

   parser.add_argument("key_id", help="Account Key",)
   parser.add_argument("key_secret_id", help="Account Secret ID",)
   parser.add_argument("--Tell", "-T", help="Tell Settings",action="store_true")
   parser.add_argument("--Verbose","-v", help="Verbose",action="store_true")
   parser = parser.parse_args()
   return (vars(parser))



def DownloadDeviceList(key_id,key_secret_id):
    host = 'api.remote.it'
    url_path = '/graphql/v1'
    content_type_header = 'application/json'

    hasMore=True
    last=""
    items_so_far=0

    body= {"query" :  "query { login { report(name: \"DeviceList\")}}"}
    content_length_header = str(len(body))
    headers = {
        'host': host,
        'path': url_path,
        'content-type': content_type_header,
        'content-length': content_length_header,
    }

    Success=False
    while not Success:
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


#    auth = HTTPSignatureAuth(
#                         key=b64decode(key_secret_id),
#                         key_id=key_id,
#                         covered_component_ids=[
#                                                '@request-target', 'host',
#                                                'date', 'content-type',
#                                                'content-length'
#                                                ],
#                         signature_algorithm=algorithms.HMAC_SHA256)
#
#    response = requests.post('https://' + host + url_path,
#                             json=body,
#                             auth=auth,
#                             headers=headers)

       if response.status_code != 200:
          sys.stderr.write("Error in Request\n")
          sys.stderr.write(response.text)
          time.sleep(20)
       else:
          Success=True  
                      

    reply=response.json()
#    pprint(reply)

    if "errors" in reply:
        sys.stderr.write("Error in Query\n")
        sys.stderr.write(reply)
        sys.exit(2)


    ReportURL=response.json()["data"] ["login"] ["report"]
#    pprint (ReportURL)

    trys=0

    while trys < 10:
        response = requests.get(ReportURL)

        if response.status_code == 200:
            break
        else:
            print("Trys: {}".format(trys))
            sys.stderr.write("Error in Request for CSV file\n")
            sys.stderr.write(response.text)
            time.sleep(20)


    if response.status_code != 200:
        sys.exit(3)


    return(response.text.splitlines())

def ProcessDeviceList(lines):
    numberOfLines=0

    deviceDetails=[]
    total_devices={}
    total_devices_id={}
    deviceID=None



    for line in lines:
        if numberOfLines == 0 :
            if line != "id,name,hardwareId,title,state,timestamp,created,address":
                sys.exit("Report does not start with id,name,hardwareId,title,state,timestamp,created,address. It starts with: {}".format(line))
        else:

#            print(line)
            fields=line.split(",")
            deviceID=fields[INTERNAL_ID]
            if deviceID in total_devices_id:
               total_devices_id[deviceID].append(fields)
            else:
               total_devices_id[deviceID]=[fields]
        numberOfLines+=1


#    pprint(total_devices_id)

    for id in total_devices_id:
       deviceID=None
#       pprint(id)
#       pprint(total_devices_id[id])
       deviceID=None
       for service in total_devices_id[id]:
#            pprint(service)
#            pprint(service[TYPE])
            if service[TYPE]=="Bulk Service":
                deviceID=service[ID]
#                print ("Have DeviceID of {}".format(deviceID))
       if deviceID == None:
           print("No bulk for ID: {}".format(id))

       if deviceID in total_devices:
          total_devices[deviceID].append(total_devices_id[id])
       else:
          total_devices[deviceID]=[total_devices_id[id]]


#            print(internalAddressStr)
#            print(device["name"],device["enabled"],device["id"],eMail,device["created"],device["lastReported"],len(device["services"]),device["owner"],internalAddressType,internalAddressStr,has_VNC_service,sep=',')
    #        if device["owner"]["email"].lower() != "civil-remot3it-provisioning-ug@trimble.com":
    #            print(device["name"],device["id"],device["owner"]["email"],device["created"],sep=',')
    #            invalid_emails+=1
#        sys.stderr.write("{} of {}\n".format(items_so_far,RemoteItJson["total"]))

#    pprint(total_devices)

    return(total_devices)


def ProcessDups (devices,Prefix):
   print ("{} Duplicates:".format(Prefix))
   for device in devices:
      if device == None:
         continue
      if device.startswith(Prefix) :
         if len(devices[device])!= 1:
            print (device)
            dups=devices[device]
#            pprint(dups)
            for dup in sorted(dups):
   #            pprint (dup)
   #            pprint (len(dup))
               print ("   {},{},{}".format(dup[0][HW_ID],dup[0][LAST_CONTACT],dup[0][CREATED]))
   #         pprint(device)
   print ("End of {} Duplicates:".format(Prefix))


def ProcessServices (devices,Prefix,Expected):
   print ("{} With incorrect number of services. Expected {}:".format(Prefix,Expected))
   for device in devices:
#      print(device)
      if device == None:
         continue
      if device.startswith(Prefix) :
         if len(devices[device]) == 1: # only non dups
            if len(devices[device][0]) != Expected: # only
               print (device, len(devices[device][0]))
               dups=devices[device][0]
#               pprint(dups)
               for dup in sorted(dups):
      #            pprint (dup)
      #            pprint (len(dup))
                  print ("   {},{},{},{}".format(dup[HW_ID],dup[0][LAST_CONTACT],dup[CREATED],dup[TYPE]))
      #         pprint(device)
   print ("End of {} With incorrect number of services.".format(Prefix))


def ProcessVNCServices (devices,Prefix):
   print ("{} With incorrect VNC Services.".format(Prefix))
   for device in devices:
#      print(device)
      if device == None:
         continue
      if device.startswith(Prefix) :
         for current_device in devices[device]:
#            print(current_device)
            for service in current_device:
#               print(service[ID])
               if service[ID] ==  "VNC":
                  pprint(service)
   #            pprint (dup)
   #            pprint (len(dup))
                  print ("   {},{},{},{}".format(service[HW_ID],service[LAST_CONTACT],service[CREATED],service[TYPE]))
   #         pprint(device)
   print ("End of {} With incorrect VNC of services.".format(Prefix))


def main():
   args=get_args()
   if args["Verbose"]:
       http_client.HTTPConnection.debuglevel = 1
   if args["Tell"]:
       sys.stderr.write("Key_Id: {}\n".format(args["key_id"]))
       sys.stderr.write("Key Secret: {}\n".format(args["key_secret_id"]))


#   print(HW_ID)
   lines=DownloadDeviceList(args["key_id"],args["key_secret_id"])

#   with open("/Users/gkirk/Documents/GitHub/Remote.It/ad38bf9d-db11-482a-b1a1-3b2edb43fe1a.csv", "r") as temp_file:
#      lines = [line.rstrip('\n') for line in temp_file]
   #.split(",")
#   pprint(lines)

#   pprint(lines[0])

   devices=ProcessDeviceList(lines)
   print("Total Devices: {}\n".format(len(devices)))

#   pprint(devices)

   ProcessDups(devices,"Tablet")
   print("\n\n")

   ProcessDups(devices,"SNM941")
   print("\n\n")

   ProcessDups(devices,"EC520")
   print("\n\n")

   ProcessServices(devices,"Tablet",2)
   print("\n\n")

#   ProcessServices(devices,"SNM941",10)
#   print("\n\n")

   ProcessServices(devices,"EC520",3)
   print("\n\n")

   ProcessVNCServices(devices,"Tablet")
   print("\n\n")




#   print("Name", "Enabled","ID", "Owner", "Created", "LastReported","Services","eMail","InternalIPType","InternalIP","VNCProblem",sep=',')


if __name__ == '__main__':
    main()

#pprint(invalid_emails)
