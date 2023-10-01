#!/usr/bin/env python3
import argparse
import sys

#cgitb.enable()


#from JCMBSoftPyLib import HTML_Unit

from RemoteIt import RemoteIt

from pprint import pprint

import csv

import os


def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Account Summary.')

   parser.add_argument("username", help="Account User name",)
   parser.add_argument("password", help="Account password",)
   parser.add_argument("key", help="Account developer key",)
   parser.add_argument("Device_ID", help="Device ID, <Model>-<Serial>")
   parser.add_argument("HW_ID", help="Hardware ID", nargs="?")
   parser.add_argument("--Tell", help="Tell Settings",action="store_true")
   parser.add_argument("--Force", help="Force Deletion, even if it is the only copy of the device in the account",action="store_true")
   parser.add_argument("--DryRun", help="Do not delete, just show what would happen",action="store_true")
   parser.add_argument("--Verbose", help="Verbose",action="store_true")

   parser = parser.parse_args()
   args={}
   args["username"]=parser.username
   args["password"]=parser.password
   args["dev_key"]=parser.key
   args["Device_ID"]=parser.Device_ID
   args["HW_ID"]=parser.HW_ID
   args["Force"]=parser.Force
   args["DryRun"]=parser.DryRun
   args["Verbose"]=parser.Verbose
#   args["HW_ID"]=args["HW_ID"].replace(":","")

   if parser.Tell :
      sys.stderr.write("Username: {}\n".format(args["username"]))
      sys.stderr.write("Password: {}\n".format(args["password"]))
      sys.stderr.write("Key: {}\n".format(args["dev_key"]))
      sys.stderr.write("Device ID : {}\n".format(args['Device_ID']))
      sys.stderr.write("HW ID : {}\n".format(args['HW_ID']))
      sys.stderr.write("Force Delete: {}\n".format(args['Force']))
      sys.stderr.write("Verbose: {}\n".format(args['Verbose']))

   return (args)



def delete_device (remoteIt,Device_ID, HW_ID, Force, DryRun, Verbose):

   if Verbose:
      sys.stderr.write("Geting Device information for {}.\n".format(Device_ID))

   remotes=remoteIt.get_devices_by_name(Device_ID)
   Found_HW_ID=False
   number_items=0
   for device in remotes["devices"]:
      if device["servicetitle"] == "Bulk Service":
         number_items+=1

   if number_items == 0:
      sys.stdout.write("{} is not registered\n".format(Device_ID))
      return(1)

   if number_items == 1:
      if Force:
         if Verbose:
            sys.stderr.write("{} is only registered once. Deleting possible due to --Force.\n".format(Device_ID))
      else:
         sys.stdout.write("{} is only registered once.\n".format(Device_ID))
         return(2)



   for device in remotes["devices"]:
      if device["servicetitle"] == "Bulk Service":

#         pprint(device)
         Found_HW_ID=(device["deviceaddress"]==HW_ID)
      if Found_HW_ID:
         break
      else:
         if Verbose:
            print("Device with different ID of {} for {} found. This is normal for duplicates".format(device["deviceaddress"],Device_ID))

   if not Found_HW_ID:
      sys.stderr.write("Device: {} is not registered with HW ID of {}. But it is registered with different HW ID's\n".format(Device_ID,HW_ID))
      return(3)
   else:
      sys.stdout.write ("Deleting: {} with hardware id of {}, ".format(Device_ID,HW_ID))
      if DryRun:
         sys.stdout.write("DryRun.\n")
      else:
         try:
             devices_details=remoteIt.delete_device(HW_ID)
             if devices_details:
                sys.stdout.write("Succeeded.\n")
             else:
                pprint(devices_details)
                sys.stdout.write("Reported as Failed, but generally deleted.\n")
         except:
            sys.stdout.write("Failed. (Timeout)\n")
      sys.stdout.flush()


def main():
   args=get_args()
   remoteIt=RemoteIt(args["username"],args["password"],args["dev_key"])


   if args["Verbose"]:
      sys.stdout.write ("Connecting to Remote.it\n")

   if not remoteIt.connect_to_remote_it():
      sys.exit("Connecting to Remote.it failed")

   if args["Verbose"]:
      sys.stdout.write ("Connected to Remote.it\n")

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
            delete_device(remoteIt,row[1],row[0],args["Force"],args["DryRun"], args["Verbose"])

   else:
      if args["HW_ID"] == None:
         sys.exit("HW Must be provided when deleting a single value")
      delete_device(remoteIt,args["Device_ID"],args["HW_ID"],args["Force"],args["DryRun"],args["Verbose"])
#   pprint(remotes)

if __name__ == '__main__':
    main()
