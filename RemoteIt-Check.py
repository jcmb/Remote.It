#!/usr/bin/env python3 -u
import json
import os
import os.path
from pprint import pprint
import argparse
import sys
from datetime import datetime
import urllib.parse
import logging
import csv
import fileinput
import glob

import cgitb
#cgitb.enable()

import collections

from JCMBSoftPyLib import HTML_Unit
import tempfile

from RemoteIt import RemoteIt


def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Account Summary.')

   parser.add_argument("username", help="Account User name",)
   parser.add_argument("password", help="Account password",)
   parser.add_argument("key", help="Account developer key",)
   parser.add_argument("--Device_ID", help="Device ID")
   parser.add_argument("--Reg", help="Registration File, file spec to check", nargs='+', type=str)
   parser.add_argument("--Verbose","-v", help="Verbose",action="store_true")

   parser = parser.parse_args()
   args={}
   args["username"]=parser.username
   args["password"]=parser.password
   args["dev_key"]=parser.key
   args["DEVICE_ID"]=parser.Device_ID
   args["Reg_File"]=parser.Reg
   args["Verbose"]=parser.Verbose
   return (args)







def main():
   args=get_args()
   remoteIt=RemoteIt(args["username"],args["password"],args["dev_key"])

   if not remoteIt.connect_to_remote_it():
      sys.exit("Connecting to Remote.it failed")

   if args["DEVICE_ID"]:
      remotes=remoteIt.get_devices_by_name(args["DEVICE_ID"])
      pprint(remotes)
      if remotes:
         if len(remotes["devices"]) != 3:
            print ("Error: {} only has {} instead of 3 services".format(args["DEVICE_ID"],len(remotes["devices"])))
      else:
         print ("Error: {} is not registered".format(args["DEVICE_ID"]))


   if args["Reg_File"]:
      current=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
      to_fix=open(current+".to_fix.csv","w")
      to_fix_regwriter = csv.writer(to_fix)
      to_fix.write('"REGISTRATION_KEY","HARDWARE_ID","DEVICE_NAME","CATEGORY_A","CATEGORY_B","CATEGORY_C","CATEGORY_D","CATEGORY_E","CATEGORY_F","CATEGORY_G","CATEGORY_H","CATEGORY_I","CATEGORY_J"\n')
      to_delete=open(current+".to_delete.csv","w")
      to_delete_regwriter = csv.writer(to_delete)
      to_delete.write('"REGISTRATION_KEY","HARDWARE_ID","DEVICE_NAME","CATEGORY_A","CATEGORY_B","CATEGORY_C","CATEGORY_D","CATEGORY_E","CATEGORY_F","CATEGORY_G","CATEGORY_H","CATEGORY_I","CATEGORY_J"\n')
      Total_Records=0
      Total_Errors=0
      Total_Not=0

      for pathname in args["Reg_File"]:
         if args["Verbose"]:
            sys.stderr.write("Processing: {}\n".format(pathname))
         Records=0
         Errors=0
         Not=0

         input_file=open(pathname,"r")
         (directory,filename)=os.path.split(pathname)

         regreader = csv.reader(input_file)
         next(regreader)
         for row in regreader:
            remotes=remoteIt.get_devices_by_name(row[2])
   #         pprint(remotes)
            Records+=1
            Total_Records+=1
            if len(remotes["devices"]) == 3:
               if args["Verbose"]:
                  sys.stderr.write ("OK: {} is registered with 3 services. From file {}\n".format(row[2],filename))
            else:
               if len(remotes["devices"]) == 0:
                  sys.stderr.write ("Error: {} is not registered. From file {}\n".format(row[2],filename))
                  to_fix_regwriter.writerow(row)
                  Not+=1
                  Total_Not+=1
               else:
                  HW_ID=None
                  for device in remotes["devices"]:
                     if device["servicetitle"] == "Bulk Service":
                        HW_ID=device["deviceaddress"]

                  sys.stderr.write ("Error: {} only has {} instead of 3 services. HW_ID: {}. From file {}\n".format(row[2],len(remotes["devices"]),HW_ID,filename))
                  to_fix_regwriter.writerow(row)
                  to_delete_regwriter.writerow(row)

                  Errors+=1
                  Total_Errors+=1

         sys.stderr.write("{} Records: {} Not Registered: {}, Errors: {} ,Good: {}\n".format(filename, Records, Not, Errors, Records-Not-Errors))
      sys.stderr.write("Total Records: {} Not Registered: {}, Errors: {} ,Good: {}\n".format(Total_Records, Total_Not, Total_Errors, Total_Records-Total_Not-Total_Errors))

#   pprint (devices_details)


if __name__ == '__main__':
    main()
