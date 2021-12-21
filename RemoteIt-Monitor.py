#!/usr/bin/env python3

import json
import os
from pprint import pprint
import argparse
import sys
from datetime import datetime, timezone
import urllib.parse
import logging
import time

import cgitb
#cgitb.enable()

import collections

from JCMBSoftPyLib import HTML_Unit
import tempfile

from RemoteIt import RemoteIt

import configparser
sys.path.append("/Users/gkirk/Documents/GitHub/DOM/Modules/");

import DOM
import dateutil.parser


try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
#http_client.HTTPConnection.debuglevel = 1


def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It and DOM Monitor.')
   parser.add_argument("--HTML", help="Output summary in HTML",type=str,nargs='?')
   parser.add_argument("--HTML1", help="Output single row HTML",type=str,nargs='?')
   parser.add_argument("--log", help="Directory store the replies from the server in that folder")
   parser.add_argument("--rate", type=int, help="Cycle check interval",default=60)
   parser.add_argument("--staging", help="Report from staging accounts",action="store_true")
   parser.add_argument("--services", type=int, help="Number of expected services",default=3)
   parser.add_argument("DeviceId", type=str,help="Device ID to report status on eg SNM941-123456")
   parser.add_argument("-v","--verbose", help="Report status",action="store_true")
   parser.add_argument("--CSV", help="Output to CSV File",type=str,nargs='?')

   parser = parser.parse_args()
   args={}
   args["HTML"]=parser.HTML
   args["HTML1"]=parser.HTML1
   args["log_dir"]=parser.log
   args["Verbose"]=parser.verbose
   args["Staging"]=parser.staging
   args["DeviceId"]="SNM941-"+parser.DeviceId

   args["Services"]=parser.services
   args["Rate"]=parser.rate
   args["CSV"]=parser.CSV

   config = configparser.ConfigParser()
   config.read('DOM.ini')

   if args["Staging"]:
      args["DOM_Key"]=config.get('Staging','Key')
      args["DOM_Secret"]=config.get('Staging','Secret')
   else:
      args["DOM_Key"]=config.get('Production','Key')
      args["DOM_Secret"]=config.get('Production','Secret')

   config.read('RemoteIt.ini')
   if args["Staging"]:
      args["RIT_Username"]=config.get('Staging','Username')
      args["RIT_Password"]=config.get('Staging','Password')
      args["RIT_Key"]=config.get('Staging','Key')
   else:
      args["RIT_Username"]=config.get('Production','Username')
      args["RIT_Password"]=config.get('Production','Password')
      args["RIT_Key"]=config.get('Production','Key')
   return (args)


def check_services(services,Expected_Services):

   Services_Count = Expected_Services==len(services)
   if not Services_Count:
      logging.warning("Incorrect number of services, Expected {} got {}".format(Expected_Services,len(services)))

   Bulk="Bulk Service" in services
   if not Bulk:
      if not Bulk:
         logging.warning("Missing Bulk Service")

   iSSH = "Internal_SSH" in services
   if not iSSH:
      logging.warning ("Missing SSH")

   iWWW = "Internal_HTTP" in services
   if not iWWW:
      logging.warning("Missing HTTP")

   if Expected_Services >=4:
      eVNC="External_VNC" in services
      if not eVNC:
         logging.warning("Missing VNC")
   else:
      eVNC=None

   return (Services_Count,Bulk,iSSH,iWWW,eVNC)


def get_remoteit_services(remoteIt,DeviceId):
   device_details=remoteIt.get_devices([DeviceId])
   active_services=remoteIt.active_services(device_details)
   active_services=remoteIt.remove_device_prefix(active_services,DeviceId)
   active_services=remoteIt.remove_duplicate_services(active_services)
   return(active_services)


def get_DOM_info(Device_DOM,DeviceId):
   positions=Device_DOM.get_position(DeviceId)

   if positions==None:
      last_position_time=None
   else:
      last_position_time=Device_DOM.latest_time(positions["positions"])
#   pprint (last_position_time)

   status=Device_DOM.get_status(DeviceId)
   if status==None:
      status=None
      pos_status_delta=None
   else:
      last_status_time=Device_DOM.latest_time(status["status"])
      if last_position_time==None:
         pos_status_delta=None
      else:
         pos_status_delta=last_position_time-last_status_time

   return(last_position_time,last_status_time,pos_status_delta)



def process_device_cycle(DeviceId,remoteIt,Device_DOM,Expected_Services,CSV_File,HTML_File,HTML1_File,Verbose=False):
   device_positions={}
   device_status={}

#   if Verbose:
#      sys.stdout.write("{}\n".format(DeviceId))

   active_services=get_remoteit_services(remoteIt,DeviceId)

   if "Bulk Service" in active_services:
      last_remoteit_time=dateutil.parser.parse(active_services["Bulk Service"]["lastcontacted"])
   else:
      last_remoteit_time=None

   (Services_Count,Bulk,iSSH,iWWW,eVNC)=check_services(active_services,Expected_Services)


   (last_position_time,last_status_time,pos_status_delta)=get_DOM_info(Device_DOM,DeviceId)

   cycle_end=datetime.now(timezone.utc)

   CSV_File.write("{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
      cycle_end,
      last_remoteit_time,
      "N/a" if last_remoteit_time == None else cycle_end-last_remoteit_time,
      last_position_time,
      "N/a" if last_position_time == None else cycle_end-last_position_time,
      last_status_time,
      "N/a" if last_status_time == None else cycle_end-last_status_time,
      pos_status_delta,
      Services_Count,
      Bulk,
      iSSH,
      iWWW,
      eVNC
      ))

   CSV_File.flush()

   sys.stdout.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
      DeviceId,
      cycle_end,
      last_remoteit_time,
      "N/a" if last_remoteit_time == None else cycle_end-last_remoteit_time,
      last_position_time,
      "N/a" if last_position_time == None else cycle_end-last_position_time,
      last_status_time,
      "N/a" if last_status_time == None else cycle_end-last_status_time,
      pos_status_delta,
      Services_Count,
      Bulk,
      iSSH,
      iWWW,
      eVNC
      ))

   HTML_File.write("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>\n".format(
      cycle_end,
      last_remoteit_time,
      "N/a" if last_remoteit_time == None else cycle_end-last_remoteit_time,
      last_position_time,
      "N/a" if last_position_time == None else cycle_end-last_position_time,
      last_status_time,
      "N/a" if last_status_time == None else cycle_end-last_status_time,
      pos_status_delta,
      Services_Count,
      Bulk,
      iSSH,
      iWWW,
      eVNC
      ))

   HTML_File.flush()

   try:
      HTML1_File.truncate()
   except:
      pass #If it is /dev/null this fails

   HTML1_File.write("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>\n".format(
      DeviceId,
      cycle_end,
      last_remoteit_time,
      "N/a" if last_remoteit_time == None else cycle_end-last_remoteit_time,
      last_position_time,
      "N/a" if last_position_time == None else cycle_end-last_position_time,
      last_status_time,
      "N/a" if last_status_time == None else cycle_end-last_status_time,
      pos_status_delta,
      Services_Count,
      Bulk,
      iSSH,
      iWWW,
      eVNC
      ))

   HTML1_File.flush()


def CSV_Header(CSV_File):

   CSV_File.write("{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
      "Time",
      "last_remoteit_time",
      "RemoteIt Delta",
      "DOM Pos",
      "DOM Pos Delta",
      "DOM Status",
      "DOM Status Delta",
      "DOM Messages Delta",
      "Services_Count",
      "Bulk",
      "iSSH",
      "iWWW",
      "eVNC"
      ))

def open_files(CSV_FileName,HTML_FileName,HTML1_FileName,DeviceId,Verbose=False):

   if CSV_FileName=="":
      CSV_FileName="{}.csv".format(DeviceId)

   if HTML_FileName=="":
#      print ("blank")
      HTML_FileName="{}.html".format(DeviceId)

   if HTML1_FileName=="":
      HTML1_FileName="{}.htm".format(DeviceId)

   if Verbose:
      print("CSV:   {}".format(CSV_FileName))
      print("HTML:  {}".format(HTML_FileName))
      print("HTML1: {}".format(HTML1_FileName))



   if CSV_FileName == None:
      CSV_File = open(os.devnull,"w")
   else:
      if os.path.isfile(CSV_FileName):
         CSV_File = open(CSV_FileName,"a")
      else:
         CSV_File = open(CSV_FileName,"w")
         CSV_Header(CSV_File)

   if HTML_FileName == None:
      HTML_File = open(os.devnull,"w")
   else:
      if os.path.isfile(HTML_FileName):
         HTML_File = open(HTML_FileName,"a")
      else:
         HTML_File = open(HTML_FileName,"w")
         HTML_Unit.output_html_header(HTML_File,"SNM941 Monitor {}".format(DeviceId))
         HTML_Unit.output_html_body(HTML_File)
         HTML_Unit.output_table_header(HTML_File,"Details","{} Details".format(DeviceId),[
            "Time",
            "last_remoteit_time",
            "RemoteIt Delta",
            "DOM Pos",
            "DOM Pos Delta",
            "DOM Status",
            "DOM Status Delta",
            "DOM Messages Delta",
            "Services_Count",
            "Bulk",
            "iSSH",
            "iWWW",
            "eVNC"])

         HTML_Header(HTML_File)

   if HTML1_FileName == None:
      HTML1_File = open(os.devnull,"w")
   else:
      HTML1_File = open(HTML1_FileName,"w")

   return (CSV_File,HTML_File, HTML1_File)



def close_files(CSV_File,HTML_File,HTML1_File):
   print ("Closing files")
   CSV_File.close()
   HTML_File.close()
   HTML1_File.close()


def main():
   args=get_args()

   remoteIt=RemoteIt(args["RIT_Username"],args["RIT_Password"],args["RIT_Key"],args["log_dir"])

   if not remoteIt.connect_to_remote_it():
      sys.exit("Connecting to Remote.it failed")

   Device_DOM=DOM.DOM(args["DOM_Key"],args["DOM_Secret"],None,staging=args["Staging"])

   (CSV_File,HTML_File,HTML1_File)=open_files(args["CSV"],args["HTML"],args["HTML1"],args["DeviceId"],args["Verbose"])
   sys.stdout.write(args["DeviceId"])
   sys.stdout.write(",")
   CSV_Header(sys.stdout)

   while True:
      try:
         cycle_start=datetime.now(timezone.utc)
         process_device_cycle(args["DeviceId"],remoteIt,Device_DOM,args["Services"],CSV_File,HTML_File,HTML1_File,args["Verbose"])
         cycle_end=datetime.now(timezone.utc)
         delta=cycle_end-cycle_start
         next_check=args["Rate"]-delta.total_seconds()
         if next_check<0:
            next_check = 0

         time.sleep(next_check)

      except KeyboardInterrupt:
         close_files(CSV_File,HTML_File,HTML1_File)
         sys.stdout.write("Bye\n")
         return()
      except:
         close_files(CSV_File,HTML_File,HTML1_File)
         raise



if __name__ == '__main__':
    main()





