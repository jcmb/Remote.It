#!/usr/bin/env python3
import requests

import logging

import json
from pprint import pprint

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

      response = requests.post(url, data=json.dumps(body), headers=headers)
      response_body = response.json()
#      pprint (response_body)

      self.token=response_body["token"]
      self.service_token=response_body["service_token"]
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

   def get_devices_by_name(self,model):

      headers = {
         "developerkey": self.dev_key,
         "token": self.token,
         "Content-Type": "application/json"
      }

      url = self.base_url + "device/find/by/name/"

      response = requests.post(url, headers=headers, json={"devicestate":"all","devicename":model})
      reply=response.json()

      self.log_reply(model,response.text)

#      pprint(reply)
      if reply["status"]=='false':
         return(None)
      else:
         return (reply)

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


   def get_devices(self,serials):
      devices_details=[]
      if serials:
         for serial in serials:
#            print (serial)
            serial_details=self.get_devices_by_name(serial)
#            pprint (serial_details)
            if serial_details==None:
               logging.critical("The Remote.it server did not return data for {}. Normally this is too many results for this prefix.".format(serial))
               devices_details=None
            else:
               devices_details +=serial_details["devices"]
#            pprint (len(devices_details))
      else:
         devices_details=get_devices(args["dev_key"],token)["devices"]
      return (devices_details)



   def get_service_details(self,devices_details, device_ids,inactive=False):
      service_details={}
#      pprint(devices_details)
      for device in devices_details:
#         pprint(device)
         if device["devicealias"].startswith(device_ids):
            if inactive or device["devicestate"]=="active" or device["devicealias"].find(" - "):
               if device["devicealias"] in service_details:
                  if device["devicestate"]=="active":
                     service_details[device["devicealias"]]=device
               else:
                  service_details[device["devicealias"]]=device
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

      response = requests.post(url, data=json.dumps(body), headers=headers)
      response_body = response.json()

#      pprint (response_body)
      return(response_body["status"])


   def transfer_device(self,hw_id,new_account):

      url = self.base_url + "developer/devices/transfer/start/";


      headers = {
          "developerkey": self.dev_key,
          "token" : self.token,
          "Content-Type": "text/plain;charset=UTF-8"

      }
      body = {
         "queue_name": "WeavedTaskQueue",
         "label": "transferring",
         "options": {"devices":hw_id, "newuser":new_account, "emails": new_account }

      }



#      print (headers)
#      print (url)
#      print (json.dumps(body))

      response = requests.post(url, data=json.dumps(body), headers=headers)
      response_body = response.json()

#      pprint (response_body)
      return(response_body["status"])

