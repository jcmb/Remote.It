#!/usr/bin/env python3
import os, stat
from pprint import pprint
import sys
import logging
import argparse
import csv
from enum import Enum
from datetime import datetime
from collections import defaultdict


def get_args():
    parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Account Summary Duplicate Report.')
    parser.add_argument('infile', type=argparse.FileType('r'), help="Full Account Report",)
    parser.add_argument("date", nargs="?", help="Date for when the device being connected. YYYY-MM-DD")

#    parser.add_argument("--Tell", "-T", help="Tell Settings",action="store_true")
#    parser.add_argument("--Verbose","-v", help="Verbose",action="store_true")
    parser = parser.parse_args()
    return (vars(parser))

def Compute_Summary(infile,DateFilter):
    reader = csv.DictReader(infile)
    devices={}
    Summary=defaultdict(int)

    for each_row in reader:
#        print(each_row)
#        print(len(each_row))
        if len(each_row) != 8:
#            print(each_row)
            sys.exit("Error: Row does not have 8 fields")

        if each_row["title"] != "Bulk Service": #If it is not enabled bulk we ignore it
            continue

        if each_row["address"] == "": #If it has never been connected we ignore it.
            continue

        if DateFilter:
            parsed_date = datetime.strptime(each_row["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
#            print(parsed_date)
            if parsed_date < DateFilter:
                continue

        model_type=each_row["name"].split('-')[0]
        Summary[model_type]+=1

        devices[each_row["name"]]=each_row


    return(Summary, devices)


def Output_Summary(Summary,devices):

    max_width = max(len(item) for item in Summary)
    Summary_Total=0

    for item in Summary:
        print(f"{item:<{max_width}} {Summary[item]:>7}")
        Summary_Total+=Summary[item]
#        print (item,Summary[item])
    print()
    print(f"{'Sum':<{max_width}} {Summary_Total:>7}")
    print(f"{'Total':<{max_width}} {len(devices):>7}")
#    print("Total",len(devices))


def main():
    args=get_args()

#    if args["Verbose"]:
#        pass
#    if args["Tell"]:
#        pass

    if args["date"]:
        DateFilter=datetime.strptime(args["date"], "%Y-%m-%d")
#        pprint(DateFilter)
    else:
        DateFilter=None
    (Summary, devices)=Compute_Summary(args["infile"],DateFilter)

#    pprint(devices)
    Output_Summary(Summary,devices)
#    print(len(devices),Summary["EC520"] + Summary["Tablet"] + Summary["SNM941"] + Summary["Unknown"])


if __name__ == '__main__':
    main()
