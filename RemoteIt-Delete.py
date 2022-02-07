#!/usr/bin/env python3
import argparse
import sys

#cgitb.enable()


from JCMBSoftPyLib import HTML_Unit

from RemoteIt import RemoteIt

from pprint import pprint


def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Account Summary.')

   parser.add_argument("username", help="Account User name",)
   parser.add_argument("password", help="Account password",)
   parser.add_argument("key", help="Account developer key",)
   parser.add_argument("Device_ID", help="Device ID, <Model>-<Serial>")
   parser.add_argument("HW_ID", help="Hardware ID")
   parser.add_argument("--Tell", help="Tell Settings",action="store_true")
   parser.add_argument("--Force", help="Force Deletion, even if it is the only copy of the device in the account",action="store_true")
   parser.add_argument("--Verbose", help="Verbose",action="store_true")

   parser = parser.parse_args()
   args={}
   args["username"]=parser.username
   args["password"]=parser.password
   args["dev_key"]=parser.key
   args["Device_ID"]=parser.Device_ID
   args["HW_ID"]=parser.HW_ID
   args["Force"]=parser.Force
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







def main():
   args=get_args()
   remoteIt=RemoteIt(args["username"],args["password"],args["dev_key"])

   if not remoteIt.connect_to_remote_it():
      sys.exit("Connecting to Remote.it failed")


   remotes=remoteIt.get_devices_by_name(args["Device_ID"])
#   pprint(remotes)
   Found_HW_ID=False
   number_items=0
   for device in remotes["devices"]:
      if device["servicetitle"] == "Bulk Service":
         number_items+=1

   if number_items == 0:
      sys.stdout.write("{} is not registered\n".format(args["Device_ID"]))
      sys.exit(1)

   if number_items == 1:
      if args["Force"]:
         if args["Verbose"]:
            sys.stderr.write("{} is only registered once. Deleting due to --Force.\n".format(args["Device_ID"]))
      else:
         sys.stdout.write("{} is only registered once.\n".format(args["Device_ID"]))
         sys.exit(2)



   for device in remotes["devices"]:
      if device["servicetitle"] == "Bulk Service":
#         pprint(device)
         Found_HW_ID=(device["hardwareid"]==args["HW_ID"])
      if Found_HW_ID:
         break

   if not Found_HW_ID:
      sys.stderr.write("Device: {} is not registered with HW ID of {}. But it is registered with different HW ID's\n".format(args["Device_ID"],args["HW_ID"]))
      sys.exit(3)
   else:
      sys.stdout.write ("Deleting: {} with hardware id of {}, ".format(args["Device_ID"],args["HW_ID"]))
      devices_details=remoteIt.delete_device(args["HW_ID"])
      if devices_details:
         sys.stdout.write("Succeeded.\n")
      else:
         sys.stdout.write("Failed.\n")
      sys.stdout.flush()

if __name__ == '__main__':
    main()
