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
    parser.add_argument("--EC520", help="Treat EC520- and EC520-W- names with the same serial as duplicates",action="store_true")

#    parser.add_argument("--CSV", help="Output Duplicates as a CSV file",action="store_true")
    parser.add_argument("--Tell", "-T", help="Tell Settings",action="store_true")
    parser.add_argument("--Verbose","-v", help="Verbose",action="store_true")
    parser = parser.parse_args()
    return (vars(parser))

def canonical_name(name, ec520):
    if not ec520:
        return name
    if name.startswith("EC520-W-"):
        return "EC520-" + name[len("EC520-W-"):]
    return name

def Check_For_Dups(infile,ec520):
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

        name_key=canonical_name(each_row["Name"],ec520)

        if name_key in devices:
#            pprint(devices[name_key])
#            if each_row["LastReported"] == "None":
#                last_reported=None
#            else:
#                last_reported=datetime.strptime(each_row["LastReported"],"%Y-%m-%dT%H:%M:%S.%f%z")

#            if devices[name_key]["LastReported"] == "None":
#                previous_last_reported = None
#            else:
#                previous_last_reported=datetime.strptime(devices[name_key]["LastReported"],"%Y-%m-%dT%H:%M:%S.%f%z")

#            if last_reported == None and previous_last_reported == None:
#                # If we have never connected on each then we want to keep the newest registered unit
#                last_reported=datetime.strptime(each_row["Created"],"%Y-%m-%dT%H:%M:%S.%f%z")
#                previous_last_reported=datetime.strptime(devices[name_key]["Created"],"%Y-%m-%dT%H:%M:%S.%f%z")
#            if last_reported == None: # current is blank so we want to do nothing with it:
#                writer.writerow(each_row)
#            elif previous_last_reported == None: #Previous was blank so we want to replace it, print out the dup files
#                writer.writerow(devices[name_key])
#                devices[name_key]=each_row

            last_created=datetime.strptime(each_row["Created"],"%Y-%m-%dT%H:%M:%S.%f%z")
            previous_last_created=datetime.strptime(devices[name_key]["Created"],"%Y-%m-%dT%H:%M:%S.%f%z")

            # Here we have two records, at least one of them is not None

            if last_created > previous_last_created: #Newer than the last one, so replace it
                dups.append(devices[name_key])
#                writer.writerow(devices[name_key])
                devices[name_key]=each_row
            else:
#                writer.writerow(each_row)
                dups.append(each_row)


        else:
            devices[name_key]=each_row
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

    (dups,fieldnames)=Check_For_Dups(args["infile"],args["EC520"])

    if args["CSV"]:
        Write_Dups_CSV(args["outfile"],dups,fieldnames)
    else:
        Write_Dups_SH(args["outfile"],dups,fieldnames)


if __name__ == '__main__':
    main()
