#!/usr/bin/env -S python3

import sys
import csv
from pprint import pprint
from collections import defaultdict
import argparse

EXPECTED = {}



def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Account Summary.')

   parser.add_argument("--Delete", "-D", help="Write delete for services instead of count. Must be used with services",action="store_true")
   parser.add_argument("--Services", "-S", help="Write services list",action="store_true")
   parser.add_argument("--Summary","-U", help="Summary of issues",action="store_true")
   parser.add_argument("--SNM941", help="Include SNM941's",action="store_true")
   parser.add_argument("--Invalid", help="Report Devices with Invalid services",action="store_true")
   parser.add_argument("--Changed", help="Report Devices with device ID's that have changed",action="store_true")
   parser = parser.parse_args()
   return (vars(parser))


def processReport(delete,checkServices,summary,invalid,changed):

    # Create a CSV reader object
    with open("DeviceList.csv","r") as inputFile:
        reader = csv.reader(inputFile)

        # Skip the header row
        header = next(reader)

        # Iterate through the rows and count the 'Bulk Service' entries
        ID = None
        devices = {}
        devicesSerial = {}
        last = {}
        created = {}
        problemDevices = defaultdict(int)

        if changed:
           print ("Orginal ID","Created","Last Contact","New ID" ,"Created", "Last Contact",sep=", ");


        for row in reader:
            ID = row[2]
            if ID in devices:
                devices[ID].append(row[1])
            else:
                devices[ID] = [row[1]]

            last[ID] = row[5]

            if ID in created:
                created[ID].append(row[6])
            else:
                created[ID] = [row[6]]


            if changed:
                deviceID = row[1]
                if row[3] == "Bulk Service":
                    hyphen_index = deviceID.rfind("-")
                    if hyphen_index != -1:
                        deviceType = deviceID[:hyphen_index]
                        serialNumber = deviceID[hyphen_index+1:]
                    else:
                        deviceType = deviceID
                        serialNumber = deviceID


        #            print("Serial:", deviceType, serialNumber)

                    if serialNumber in devicesSerial:
                        if devicesSerial[serialNumber][0] != deviceType:
                            if row[6] < devicesSerial[serialNumber][1]:
                                print (deviceID, row[6],row[5], devicesSerial[serialNumber][0],devicesSerial[serialNumber][1],devicesSerial[serialNumber][2], sep=", ")
                            else:
                                print (devicesSerial[serialNumber][0], devicesSerial[serialNumber][1],  devicesSerial[serialNumber][2], deviceID, row[6], row[5],sep=", ")
                    else:
                        devicesSerial[serialNumber] = [deviceID,row[6],row[5]]

    #    pprint(devicesSerial)
    #    pprint(created)
        if checkServices and not delete:
            print("Hardware ID, Device Type, Device-ID, Services, Created");

        for device in devices:
            #    pprint(device)
            services = len(devices[device])
            deviceID = devices[device][services - 1]

            hyphen_index = deviceID.rfind("-")
            if hyphen_index != -1:
                deviceType = deviceID[:hyphen_index]
                serialNumber = deviceID[hyphen_index+1:]
            else:
                deviceType = deviceID
                serialNumber = deviceID


    #        print(deviceType, serialNumber)

            if checkServices or summary:
#                print (EXPECTED)
                if deviceType in EXPECTED:
    #                print(devices, services)
                    if not (services in EXPECTED[deviceType]):
                        problemDevices[deviceType] += 1
                        if checkServices:
                            if delete:
                                print("./RemoteIt-Delete.py --Force @parameters/RemoteIt.Params {} {}".format(devices[device][services - 1], device))
                            else:
                                print(
                                    device,
                                    " , ",
                                    deviceType,
                                    ",",
                                    devices[device][services - 1],
                                    ",",
                                    services,
                                    ",",
                                    created [device][len(devices[device])-1]
                                )


        if invalid:
            print("Device-ID, Serial, Web-Valid, Web-Valid_Create, Web_No_Serial, Web_No_Serial_Create, SSH_22 Valid, SSH_22 Valid_Create, SSH_22_No_Serial, SSH_22_No_Serial_Create, Last Contact, Bulk Created, Version, Location")

            for device in devices:
                #    pprint(device)
                services = len(devices[device])
                deviceID = devices[device][services - 1]
                hyphen_index = deviceID.find("-")
                deviceSerial = deviceID
                if deviceSerial.startswith("EC520-W"):
                    deviceSerial=deviceSerial[8:]
                elif deviceSerial.startswith("EC520"):
                    deviceSerial=deviceSerial[6:]




                if "EC520-_Web_Proxy_80" in devices[device]:
        #            pprint(devices[device])
                    print(deviceID,end='')
                    print(" , " , deviceSerial,end='')
                    print(" , " , str(deviceID+"_Web_Proxy_80" in devices[device]),end='')
                    try:
                        print(" , ", created[device][devices[device].index(deviceID+"_Web_Proxy_80")],end='')
                    except:
                        print(" , ",end='')
                    print(" , " , str("EC520-_Web_Proxy_80" in devices[device]),end='')
                    try:
                        print(" , ", created[device][devices[device].index("EC520-_Web_Proxy_80")],end='')
                    except:
                        print(" , ",end='')

                    print(" , " , str(deviceID+"_SSH_22" in devices[device]),end='')
                    try:
                        print(" , ", created[device][devices[device].index(deviceID+"_SSH_22")],end='')
                    except:
                        print(" , ",end='')
                    print(" , " , str("EC520-_SSH_22" in devices[device]),end='')
                    try:
                        print(" , ", created[device][devices[device].index("EC520-_SSH_22")],end='')
                    except:
                        print(" , ",end='')
                    print(" , " , last [device],end='')
                    print(" , " , created [device][len(devices[device])-1])



        #    , str(len(device)))
    #    pprint(problemDevices)
        if summary:
            for device, total in problemDevices.items():
                print(f"{device}: {total}")
    #    pprint(problemDevices)
        # Print the count
        # print("Number of 'Bulk Service' devices:", bulk_service_count)

def main():
    global EXPECTED
    args=get_args()
    if args["SNM941"]:
        EXPECTED = {"EC520": [3], "SNM941": [11,12], "Tablet": [2]}
#        EXPECTED = {"EC520": [3], "SNM941": [11], "Tablet": [2]}
    else:
        EXPECTED = {"EC520": [3], "Tablet": [2]}

    processReport(args["Delete"],args["Services"],args["Summary"],args["Invalid"],args["Changed"])


if __name__ == '__main__':
    main()
