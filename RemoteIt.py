#!/usr/bin/env python3
import requests


import logging

import json
from pprint import pprint

from datetime import datetime

try:
    import http.client as http_client
except ImportError:
    # Python 2, not tested any longer
    import httplib as http_client



class RemoteIt(object):
   def __init__(self, username,password,dev_key, logging_dir=None, timeout=5, base_url="https://api.remot3.it/apv/v27/",verbose=False):
      self.base_url=base_url
      self.timeout=timeout
      self.username=username
      self.password=password
      self.dev_key=dev_key
      self.log_dir=logging_dir
      self.token=None
      self.serivce_token=None
      self.verbose=verbose
      self.reason=None

      if self.verbose:
         logging.getLogger("requests").setLevel(logging.DEBUG)
         http_client.HTTPConnection.debuglevel = 1
      else:
         logging.getLogger("requests").setLevel(logging.WARNING)



   def set_logging(self,logging_dir):
      self.log_dir=logging_dir

   def connect_to_remote_it(self):
      headers = {
          "developerkey": self.dev_key
      }
      body = {
          "password": self.password,
          "username": self.username
      }
      url = self.base_url +"user/login"

      response = requests.post(url, data=json.dumps(body), headers=headers,timeout=60)
      response_body = response.json()
#      pprint (response_body)

      if "token" in response_body:
          self.token=response_body["token"]
          self.service_token=response_body["service_token"]
          self.reason=""
      else:
          self.token=None
          self.reason=response_body["reason"]
      return(self.token!=None)

   def log_reply(self,model,reply):
      if self.log_dir == None:
         return

      log_file_dir=self.log_dir+"/"+model
      log_file_name=log_file_dir+"/"+datetime.now().strftime("%Y-%m-%d--%H-%M-%S")+".json"
      if not os.path.exists(log_file_dir):
         os.makedirs(log_file_dir)

      log=open(log_file_name,"w")
      log.write(reply)
      log.close()


   def get_all_devices(self):

      headers = {
         "developerkey": self.dev_key,
         "token": self.token,
         "Content-Type": "application/json"
      }

      url = self.base_url + "device/find/by/name/"

      response = requests.post(url, headers=headers, json={"devicestate":"all"},timeout=45)
      reply=response.json()

#      pprint(reply)

      self.log_reply("All",response.text)

      if reply["status"]=='false':
         return(None)
      else:
         return (reply)


   def get_devices_by_name(self,model,verbose=False):

      headers = {
         "developerkey": self.dev_key,
         "token": self.token,
         "Content-Type": "application/json"
      }

      url = self.base_url + "device/find/by/name/"


      if verbose:
         print(model)

      try:
         response = requests.post(url, headers=headers, json={"devicestate":"all","devicename":model},timeout=45)
         reply=response.json()
      except:
          return(None)


      self.log_reply(model,response.text)

      if verbose:
          pprint(reply)

      if "status" in reply:
          if reply["status"]=='false':
              return(None)
          else:
              return (reply)
      else:
          return(None)


   def get_device_ids (self,devices_details, serials):
      active_devices=set()
      inactive_devices=set()

   #   pprint (devices_details)
   #   pprint (serials)

      if serials==("",):
         for device in devices_details:
            if device["servicetitle"] == "Bulk Service":
               if device["devicestate"] == "active":
                  devices+= [device["devicealias"]]
      else:
         for device in devices_details:
            if device["devicealias"].startswith(serials):
               if device["servicetitle"] == "Bulk Service":
                  if device["devicestate"] == "active":
                     active_devices.add(device["devicealias"])
                  else:
                     inactive_devices.add(device["devicealias"])

      active_devices=sorted(active_devices)
      for device in active_devices:
         if device in inactive_devices:
            inactive_devices.remove(device)
      inactive_devices=sorted(inactive_devices)
      return (active_devices,inactive_devices)


   def duplicate_services(self,device_details):
      service_names=collections.defaultdict(int)
      active_service_names=collections.defaultdict(int)
      service_ids=collections.defaultdict(int)

      for service in device_details:
         service_names[service["devicealias"]]+=1
         if service["devicestate"]=="active":
            active_service_names[service["devicealias"]]+=1
         service_ids[service["deviceaddress"]]+=1

      return(service_names,active_service_names,service_ids)

   def remove_duplicate_services(self,device_details): #Returns a Dictionary
      de_dupped_services={}
      for service in device_details:
         if service["devicealias"] in  de_dupped_services: #Always update if the service is active so that if one service is active it will be reported
            if service["devicestate"] == "active":
               de_dupped_services[service["devicealias"]]=service
         else:
            de_dupped_services[service["devicealias"]]=service
#      pprint(list(de_dupped_services.values()))
      return(de_dupped_services)

      service_names=collections.defaultdict(int)
      active_service_names=collections.defaultdict(int)
      service_ids=collections.defaultdict(int)

      for service in device_details:
         service_names[service["devicealias"]]+=1
         if service["devicestate"]=="active":
            active_service_names[service["devicealias"]]+=1
         service_ids[service["deviceaddress"]]+=1

      return(service_names,active_service_names,service_ids)


   def remove_device_prefix(self,device_details,DeviceId):
#      pprint(device_details)
      Device_Prefix=DeviceId+" - "
      for service in device_details:
         if  service["devicealias"] == DeviceId:
            service["devicealias"]="Bulk Service"
         else:
            service["devicealias"]=service["devicealias"].replace(Device_Prefix,"")
#      pprint(device_details)
      return(device_details)



   def active_services(self,device_details):
      active_services=[]
      for service in device_details:
         if service["devicestate"] == "active":
            active_services+=[service]
#      pprint(active_services)
      return(active_services)


   def get_devices(self,serials,verbose=False):
      devices_details=[]
      if serials:
         for serial in serials:
            if verbose:
                print (serial)
            serial_details=self.get_devices_by_name(serial)
            if verbose:
               pprint (serial_details)
            if serial_details==None:
               logging.critical("The Remote.it server did not return data for {}. This may be becuase there are too many results for this prefix.".format(serial))
#               devices_details=None
            else:
               devices_details +=serial_details["devices"]
#            pprint (len(devices_details))
      else:
         devices_details=self.get_all_devices()
#         devices_details=get_devices(args["dev_key"],token)["devices"]
      return (devices_details)



   def get_service_details(self,devices_details, device_ids,inactive=False):
      service_details={}
      hardware_id_details={}
#      pprint(devices_details)
      for device in devices_details:
#         pprint(device)
#         pprint(hardware_id_details)
#         print (device["hardwareid"] in hardware_id_details)
         if device["devicealias"] == "VNC":
            device["devicealias"] = hardware_id_details[device["hardwareid"]]["devicealias"] + " - VNC - Missing Device ID"
         if device["devicealias"].startswith(device_ids) or (device["hardwareid"] in hardware_id_details):
            if inactive or device["devicestate"]=="active": # or device["devicealias"].find(" - "):
               if device["devicealias"] in service_details:
#                  print(datetime.strptime(device["lastcontacted"],"%Y-%m-%dT%H:%M:%S.%f%z"))
                  if datetime.strptime(device["lastcontacted"],"%Y-%m-%dT%H:%M:%S.%f%z") > datetime.strptime(service_details[device["devicealias"]]["lastcontacted"],"%Y-%m-%dT%H:%M:%S.%f%z"):
                     service_details[device["devicealias"]]=device
                     hardware_id_details[device["hardwareid"]]=device
               else:
                  service_details[device["devicealias"]]=device
                  hardware_id_details[device["hardwareid"]]=device
      return(service_details)

   def get_service_details_with_dups(self,devices_details, device_ids):
      service_details={}
      hardware_id_details={}
#      print("Start Device Details")
#      pprint(devices_details)
#      print("End Device Details")
      for device in devices_details:

#         pprint(device)
#         print (device["hardwareid"] in hardware_id_details)
#         if device["devicealias"] == "VNC":
#            device["devicealias"] = hardware_id_details[device["hardwareid"]]["devicealias"] + " - VNC - Missing Device ID"

         if device["devicealias"].startswith(device_ids)  or  device["hardwareid"] in hardware_id_details:
            if device["servicetitle"]=="Bulk Service" :
                service_details[device["devicealias"]]=device
            else:
                service_details[device["devicealias"]+":"+device["hardwareid"]]=device
            hardware_id_details[device["hardwareid"]]=device
#      print("Start Service Details")
#      print(service_details)
#      print("End Service Details")
      return(service_details)


   def get_duplicate_devices(self,devices_details, device_id):
      device_details={}
#      pprint(devices_details)
      for device in devices_details:
         if device["devicealias"].startswith(device_id):
            if device["servicetitle"]=="Bulk Service":
               device_details[device["deviceaddress"]]=device

#      pprint(device_details)
      return(device_details)


   def delete_device(self,hw_id):
      headers = {
          "developerkey": self.dev_key,
          "token" : self.token,
          "Content-Type": "text/plain;charset=UTF-8"

      }
      body = {
      }


      url = self.base_url +"developer/device/delete/registered/" + hw_id

#      print (headers)
#      print (url)

      response = requests.post(url, data=json.dumps(body), headers=headers,timeout=45)
      response_body = response.json()
#      pprint(response_body)

      result=False
      if response_body != None:
         result = response_body["status"]=="true"
      return(result)

