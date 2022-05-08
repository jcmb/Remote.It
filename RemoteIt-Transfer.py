#!/usr/bin/env python3
import argparse
import sys

#cgitb.enable()


from JCMBSoftPyLib import HTML_Unit

from RemoteIt import RemoteIt

from pprint import pprint


def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Account Summary.')

   parser.add_argument("user", help="Current Account email",)
   parser.add_argument("password", help="Current Account password",)
   parser.add_argument("dev_key", help="Current Account dev_key",)
   parser.add_argument("New_Account", help="Acount to transger to")
   parser.add_argument("Device_ID", help="Device ID, <Model>-<Serial>")
   parser.add_argument("HW_ID", help="Hardware ID")
   parser.add_argument("-T","--Tell", help="Tell Settings",action="store_true")
   parser.add_argument("-V","--Verbose", help="Verbose",action="store_true")

   parser = parser.parse_args()
   args={}
   args["username"]=parser.user
   args["password"]=parser.password
   args["dev_key"]=parser.dev_key
   args["Device_ID"]=parser.Device_ID
   args["HW_ID"]=parser.HW_ID
   args["Dest_Email"]=parser.New_Account
   args["Verbose"]=parser.Verbose
#   args["HW_ID"]=args["HW_ID"].replace(":","")

   if parser.Tell :
      sys.stderr.write("User: {}\n".format(args["username"]))
      sys.stderr.write("Password: {}\n".format(args['password']))
      sys.stderr.write("Dev Key: {}\n".format(args['dev_key']))
      sys.stderr.write("Device ID : {}\n".format(args['Device_ID']))
      sys.stderr.write("HW ID: {}\n".format(args['HW_ID']))
      sys.stderr.write("New Account: {}\n".format(args['Dest_Email']))
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


   for device in remotes["devices"]:
      if device["servicetitle"] == "Bulk Service":

#         pprint(device)
         Found_HW_ID=(device["hardwareid"]==args["HW_ID"])
      if Found_HW_ID:
         break
      else:
         if args["Verbose"]:
            print("Device with different ID of {}".format(device["hardwareid"]))

   if not Found_HW_ID:
      sys.stderr.write("Device: {} is not registered with HW ID of {}. But it is registered with different HW ID's\n".format(args["Device_ID"],args["HW_ID"]))
      sys.exit(3)
   else:
      sys.stdout.write ("Transfering: {} with hardware id of {}, to {},".format(args["Device_ID"],args["HW_ID"],args["Dest_Email"]))
      devices_details=False
      devices_details=remoteIt.transfer_device(args["HW_ID"],args["Dest_Email"])
#      devices_details=remoteIt.delete_device(args["HW_ID"])
      if devices_details:
         sys.stdout.write("Succeeded.\n")
      else:
         sys.stdout.write("Failed.\n")
      sys.stdout.flush()

if __name__ == '__main__':
    main()
