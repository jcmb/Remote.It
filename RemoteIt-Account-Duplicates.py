#!/usr/bin/env python3
import os, stat
from pprint import pprint
import sys
import logging
import argparse
import csv
from enum import Enum
from datetime import datetime


def get_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Account Summary Duplicate Report.')
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('outfile', type=argparse.FileType('w'))

    parser.add_argument("--CSV", help="Output Duplicates as a CSV file. Otherwise output as a delete script",action="store_true")

#    parser.add_argument("--CSV", help="Output Duplicates as a CSV file",action="store_true")
    parser.add_argument("--Tell", "-T", help="Tell Settings",action="store_true")
    parser.add_argument("--Verbose","-v", help="Verbose",action="store_true")
    parser = parser.parse_args()
    return (vars(parser))

def Check_For_Dups(infile):
    reader = csv.DictReader(infile)
    devices={}
    dups=[]
    for each_row in reader:
#        print(each_row)
#        print(len(each_row))
        if each_row["Enabled"] != "True": #If it is not enabled we skip it, this should never be the case
            continue

        if len(each_row) != 11:
#            print(each_row)
            sys.exit("Error: Row does not have 11 fields")

        if each_row["Name"] in devices:
#            pprint(devices[each_row["Name"]])
#            if each_row["LastReported"] == "None":
#                last_reported=None
#            else:
#                last_reported=datetime.strptime(each_row["LastReported"],"%Y-%m-%dT%H:%M:%S.%f%z")

#            if devices[each_row["Name"]]["LastReported"] == "None":
#                previous_last_reported = None
#            else:
#                previous_last_reported=datetime.strptime(devices[each_row["Name"]]["LastReported"],"%Y-%m-%dT%H:%M:%S.%f%z")

#            if last_reported == None and previous_last_reported == None:
#                # If we have never connected on each then we want to keep the newest registered unit
#                last_reported=datetime.strptime(each_row["Created"],"%Y-%m-%dT%H:%M:%S.%f%z")
#                previous_last_reported=datetime.strptime(devices[each_row["Name"]]["Created"],"%Y-%m-%dT%H:%M:%S.%f%z")
#            if last_reported == None: # current is blank so we want to do nothing with it:
#                writer.writerow(each_row)
#            elif previous_last_reported == None: #Previous was blank so we want to replace it, print out the dup files
#                writer.writerow(devices[each_row["Name"]])
#                devices[each_row["Name"]]=each_row

            last_created=datetime.strptime(each_row["Created"],"%Y-%m-%dT%H:%M:%S.%f%z")
            previous_last_created=datetime.strptime(devices[each_row["Name"]]["Created"],"%Y-%m-%dT%H:%M:%S.%f%z")

            # Here we have two records, at least one of them is not None

            if last_created > previous_last_created: #Newer than the last one, so replace it
                dups.append(devices[each_row["Name"]])
#                writer.writerow(devices[each_row["Name"]])
                devices[each_row["Name"]]=each_row
            else:
#                writer.writerow(each_row)
                dups.append(each_row)


        else:
            devices[each_row["Name"]]=each_row
    return(dups,reader.fieldnames)


def Write_Dups_CSV(outfile,dups,fieldnames):
    writer = csv.DictWriter(outfile,fieldnames)
    writer.writeheader()

    for dup in dups:
        writer.writerow(dup)

def Write_Dups_SH(outfile,dups,fieldnames):
    outfile.write("PATH=$PATH:.\n")
    for dup in dups:
        outfile.write(f'RemoteIt-Delete.py @RemoteIt.Params {dup["Name"]} {dup["ID"]}\n')

    os.chmod(outfile.name, stat.S_IRWXU)



def main():
    args=get_args()

    if args["Verbose"]:
        pass
    if args["Tell"]:
        pass

    (dups,fieldnames)=Check_For_Dups(args["infile"])

    if args["CSV"]:
        Write_Dups_CSV(args["outfile"],dups,fieldnames)
    else:
        Write_Dups_SH(args["outfile"],dups,fieldnames)


if __name__ == '__main__':
    main()
