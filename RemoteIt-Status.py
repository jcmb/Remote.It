#!/usr/bin/env python3

import argparse

from pprint import pprint
import logging
import sys
import urllib
from datetime import datetime

try:
   from JCMBSoftPyLib import HTML_Unit
   HTML_Unit_Loaded=True
except:
   HTML_Unit_Loaded=False


import tempfile

from RemoteIt import RemoteIt


def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Account Summary.')
   parser.add_argument("-a","--all", help="Report all devices, not just active ones",action="store_true")
   parser.add_argument("-s","--services", help="Report all services, not just active ones",action="store_true")
   parser.add_argument("--html", help="Output in HTML format not text",action="store_true")
   parser.add_argument("--units", help="Write Units file in the temp directory",action="store_true")
   parser.add_argument("--log", help="Directory to store the replies from the server in that folder")
   parser.add_argument("--nolinks", help="Don't provide links to connect to the devices",action="store_true")
#   parser.add_argument("--preregistered", help="The device was activated into the platform using the pre-registration system",action="store_true")

   parser.add_argument("username", help="Account User name",)
   parser.add_argument("password", help="Account password",)
   parser.add_argument("key", help="Account developer key",)
   parser.add_argument("model", nargs="+", help="Filter results by model(s)")

   parser = parser.parse_args()
   args={}
   args["model"]=tuple(dict.fromkeys(parser.model))
   args["all"]=parser.all
   args["services"]=parser.services
   args["html"]=parser.html
   args["units"]=parser.units
   args["log_dir"]=parser.log
   args["username"]=parser.username
   args["password"]=parser.password
   args["dev_key"]=parser.key
   args["nolinks"]=parser.nolinks
#CLI   args["CLI"]=not parser.preregistered
#   pprint (args)
#   sys.exit(0)
   return (args)



def write_Units_File(Units_Filename,all_devices):

   if Units_Filename == None:
      Units_File=open(os.devnull, 'w')
   else:
      Units_File=open(Units_Filename,'w')

   for device in all_devices:
      Units_File.write("{}\n".format(device))

   Units_File.close()



def output_device_info (devices_details,missing_devices,device_ids,all_devices,all_services):
#   pprint(devices_details)
   for device in devices_details:
#      pprint (device)
      if device["devicealias"].startswith(device_ids):
         if device["servicetitle"] == "Bulk Service":
            if device["devicestate"] != "active":
               continue

         if device["devicestate"] =="active" or all_services:
            if device["servicetitle"] == "Bulk Service":
               print ("{:35s}     {:12s} {:8s} {:22s} {:22s} {}".format(device["devicealias"],device["servicetitle"],device["devicestate"],device["lastinternalip"],device["devicelastip"],device["deviceaddress"]))
            else:
               print ("    {:35s} {:12s} {:8s} {:22s} {:22s} {}".format(device["devicealias"],device["servicetitle"],device["devicestate"],device["lastinternalip"],device["devicelastip"],device["deviceaddress"]))

   if all_devices:
     for device in devices_details:
        if device["devicealias"].startswith(device_ids):
           if device["servicetitle"] == "Bulk Service":
              if device["devicestate"] == "inactive":
                 print(device["devicealias"], "Inactive", device["lastcontacted"],device["deviceaddress"])
     for device in missing_devices:
        print(device, "Not Registered")
      #         pprint(device)



def output_device_info_html (HTML_File,services_details,device_ids,all_devices,all_services,nolinks,missing_devices):


#   service_details=sorted(services_details)
#   pprint(services_details)

   HTML_Unit.output_table_header(HTML_File,"Devices","Devices",["Device","Active","Internal IP","External IP","Last Contact","Device Address"])

   for device in device_ids:
      if device in services_details:
         service=services_details[device]
         if service["servicetitle"] == "Bulk Service":
             if service["devicestate"] =="active":
                HTML_Unit.output_table_row(HTML_File,['<a href="#{0}">{0}</a>'.format(service["devicealias"]), service["devicestate"],service["lastinternalip"],service["devicelastip"],service["lastcontacted"],service["deviceaddress"]])
             else:
                if all_devices:
                   HTML_Unit.output_table_row(HTML_File,['{0}'.format(service["devicealias"]), service["devicestate"],service["lastinternalip"],service["devicelastip"],service["lastcontacted"],service["deviceaddress"]])
      else:
         if all_devices:
            HTML_Unit.output_table_row(HTML_File,[device, "Not Registered"])


   HTML_Unit.output_table_footer(HTML_File)

   if len(missing_devices) != 0:
      HTML_File.write("<br/><hr><br/>")
      HTML_Unit.output_table_header(HTML_File,"Unregistered","Unregistered",["Device"])

      for device in missing_devices:
         if all_devices:
            HTML_Unit.output_table_row(HTML_File,[device])

      HTML_Unit.output_table_footer(HTML_File)
      HTML_File.write("<br/><hr><br/>")

   for current_device in device_ids:
#      print ("Current")
#      print(current_device)
#      print ("Service")
#      pprint(services_details)
      if not current_device in services_details:
         continue

      device_details=services_details[current_device]

      if device_details["devicestate"] =="active" or all_services:
         HTML_File.write("<h3>{}</h3>".format(current_device))
         HTML_Unit.output_table_header(HTML_File,current_device,"{} connected at {} from {}".format(current_device,device_details["lastcontacted"],device_details["devicelastip"]),["Service Name", "State", "Type", "Device Address"])

         device_prefix=current_device

         for service_index in services_details:
            if services_details[service_index]["devicealias"].startswith(device_prefix) and (services_details[service_index]["devicealias"] != device_prefix):
# Only services that are not the bulk service get printed. The Bulk is the device name
#               print ("Service")
#               pprint(service_index)
#               print (device_prefix)
#               print (services_details[service_index]["devicealias"])
               device=services_details[service_index]
#               print(device["devicealias"])
               device["devicealias"]=device["devicealias"].replace(device_prefix+" - ","")
               device["devicealias"]=device["devicealias"].replace(device_prefix+"_","")
#               print(device["devicealias"])

               if all_services:
                  if device["devicestate"] =="active":
                     if nolinks:
                        HTML_Unit.output_table_row(HTML_File,[
                           device["devicealias"],
                           device["devicestate"],
                           device["servicetitle"],
                           device["deviceaddress"]])
                     else:
#                        print(device["devicealias"])
                        if device["devicealias"] == "VNC" :
                           HTML_Unit.output_table_row(HTML_File,[
                              '<a href="/cgi-bin/remote_connect?Address={}&Type={}">{}</a>'.format(urllib.parse.quote(device["deviceaddress"]), urllib.parse.quote(device["devicealias"]), device["devicealias"]),
                              device["devicestate"],
                              device["servicetitle"],
                              device["deviceaddress"]])
                        else:
                           HTML_Unit.output_table_row(HTML_File,[
                              '<a href="/cgi-bin/remote_connect?Address={}&Type={}">{}</a>'.format(urllib.parse.quote(device["deviceaddress"]), urllib.parse.quote(device["servicetitle"]), device["devicealias"]),
                              device["devicestate"],
                              device["servicetitle"],
                              device["deviceaddress"]])
                           
                  else:
                     HTML_Unit.output_table_row(HTML_File,[
                        device["devicealias"],
                        device["devicestate"],
                        device["servicetitle"],
                        device["deviceaddress"]])
               else:
                  if device["devicestate"] =="active":
                     if nolinks:
                        HTML_Unit.output_table_row(HTML_File,[
                           device["devicealias"],
                           device["devicestate"],
                           device["servicetitle"],
                           device["deviceaddress"]])
                     else:
                        HTML_Unit.output_table_row(HTML_File,[
                           '<a href="/cgi-bin/remote_connect?Address={}&Type={}">{}</a>'.format(urllib.parse.quote(device["deviceaddress"]), urllib.parse.quote(device["servicetitle"]), device["devicealias"]),
                           device["devicestate"],
                           device["servicetitle"],
                           device["deviceaddress"]])
         HTML_Unit.output_table_footer(HTML_File)
         HTML_File.write("<br/>")

#   HTML_Unit.output_table_header(HTML_File,"Inactive_Devices","Inactive Devices",["Device","Internal IP","External IP","Last Contact","Device Address"])
#   HTML_Unit.output_table_footer(HTML_File)
   HTML_File.write("<br/><hr><br/>")




def main(HTML_Unit_Loaded):
   args=get_args()
   if args["html"]:
      import cgitb
      cgitb.enable()
      if  not HTML_Unit_Loaded:
         sys.exit("JCMBSoftPyLib is not installed. You need to download it from https://github.com/jcmb/JCMBSoftPyLib")
      
   
   remoteIt=RemoteIt(args["username"],args["password"],args["dev_key"],args["log_dir"])

   if not remoteIt.connect_to_remote_it():
      sys.exit("Connecting to Remote.it failed")
   devices_details=remoteIt.get_devices(args["model"])
#   pprint (devices_details)

   if devices_details==None:
      sys.exit("No Devices in the Remote.it account")

   active_devices,inactive_devices=remoteIt.get_device_ids (devices_details,args["model"])

   all_devices=active_devices+inactive_devices
   
   missing_devices=[]

   for serial in args["model"]:
      if not serial in all_devices:
         missing_devices+=[serial]

#   pprint(missing_devices)

   if args["units"]:
      write_Units_File(tempfile.gettempdir()+"/Units",all_devices)

   if args["all"]:
      report_devices=all_devices
   else:
      report_devices=active_devices

#   pprint (report_devices)

   if args["services"]:
      services_details=remoteIt.get_service_details(devices_details, tuple(all_devices),args["services"])
#      pprint(device_details)
   else:
      services_details=remoteIt.get_service_details(devices_details, tuple(active_devices),args["services"])



   if args["html"]:
      HTML_File=sys.stdout;
      HTML_Unit.output_html_header(HTML_File,"Remote Devices")
      HTML_Unit.output_html_body(HTML_File)

      output_device_info_html(HTML_File,services_details,report_devices,args["all"],args["services"],args["nolinks"],missing_devices)

      for device  in report_devices:
         device_details=remoteIt.get_duplicate_devices(devices_details, device)
         
         if len (device_details) == 0:
           HTML_File.write("<br>{}: Not registered<br>\n".format(device))
         elif len (device_details) == 1:
           HTML_File.write("<br>{}: Registered<br>\n".format(device))
         else :
           HTML_File.write("<br>{}: Registered {} times<br>\n".format(device,len(device_details)))
           HTML_Unit.output_table_header(HTML_File,device,"{} duplicate registrations".format(device),["Device Address","Last Contact","Active"])
           for dev in device_details:
               HTML_Unit.output_table_row(HTML_File,[device_details[dev]["deviceaddress"],device_details[dev]["lastcontacted"],device_details[dev]["devicestate"]])
           HTML_Unit.output_table_footer(HTML_File)
      
      HTML_File.write("Generated: {}".format(datetime.now()))
      HTML_Unit.output_html_footer(HTML_File,["Devices","Active_Services","unregistered"])
   else:
      output_device_info(devices_details,missing_devices,args["model"],args["all"],args["services"])
#      pass


if __name__ == '__main__':
    main(HTML_Unit_Loaded)
