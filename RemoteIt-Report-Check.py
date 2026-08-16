#!/usr/bin/env -S python3
# pylint: disable=C0301,C0103,W0702,C0209

"""
This module provides a command-line interface for summarizing issues,
including specific device reports and service management of the Remote.it production account
"""


import sys
import csv
from pprint import pprint
from collections import defaultdict
import argparse
import datetime

try:
    from JCMBSoftPyLib import HTML_Unit

    HTML_Available = True
except:
    HTML_Available = False


EXPECTED = {}


def get_args():
    """
    Process the arguments.
    """

    #    global HTML_Available
    parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@", description="Remote.It Account Summary."
    )

    parser.add_argument(
        "--Summary", "-U", help="Summary of issues", action="store_true"
    )
    parser.add_argument("--SNM941", help="Include SNM941's", action="store_true")
    parser.add_argument(
        "--Delete",
        "-D",
        help="Write delete for services instead of count. Must be used with services",
        action="store_true",
    )

    if HTML_Available:
        parser.add_argument("--HTML", help="Include SNM941's", action="store_true")

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--Services", "-S", help="Write services list", action="store_true"
    )
    group.add_argument(
        "--Invalid", help="Report Devices with Invalid services", action="store_true"
    )
    group.add_argument(
        "--Changed",
        help="Report Devices with device ID's that have changed",
        action="store_true",
    )

    group.add_argument(
        "--Details",
        help="Report All device and services in the account. Written to DeviceList.html",
        action="store_true",
    )
    
    group.add_argument(
        "--Devices",
        help="Report All devices in the account. Written to DeviceList.html",
        action="store_true",
    )

    args = parser.parse_args()

    #   pprint(parser)
    if not any(
        value for key, value in vars(args).items() if key not in ["HTML", "SNM941"]
    ):
        parser.error(
            "No arguments provided. At least one option must be entered (excluding SNM941 and HTML)."
        )

    if args.Delete and not args.Services:
        parser.error("--Delete (-D) can only be used with --Services (-S)")

    if args.Delete and args.HTML:
        parser.error("--Delete (-D) can not be used with --HTML")

    return vars(args)


# Yes this is huge and should be refactored
# pylint: disable=R0913,R0914,R1702,R0912,R0915


def FullReport(FullDetails=True):
    TABLES = []
    with open("DeviceList.csv", "r", encoding="utf-8") as inputFile:
        reader = csv.reader(inputFile)
        HTML_File = open("DeviceList.html", "w", encoding="utf-8")
        HTML_Unit.output_html_header(HTML_File, "Remote.it Account")
        HTML_Unit.output_html_body(HTML_File)

        HTML_File.write("<h2>Created: ")
        utc_time = datetime.datetime.now(datetime.timezone.utc)
        HTML_File.write(f"{utc_time.strftime('%A, %B %d, %Y at %I:%M:%S %p %Z')}")            
        HTML_File.write("</h2>")
        

        # Skip the header row
        # pylint: disable=W0612
        header = next(reader)
        HTML_Unit.output_table_header(
            HTML_File,
            "Details",
            "Account Details",
            [
                "id",
                "name",
                "hardwareId",
                "title",
                "state",
                "timestamp",
                "created",
                "address",
            ],
        )
        TABLES.append("Details")

        for row in reader:
#            pprint(row)
            if FullDetails:
                HTML_Unit.output_table_row(HTML_File, row)
            else:
                if row[3] == "Bulk Service":
                    HTML_Unit.output_table_row(HTML_File, row)


        HTML_Unit.output_table_footer(HTML_File)
        HTML_File.write("<h2>Completed: ")
        utc_time = datetime.datetime.now(datetime.timezone.utc)
        HTML_File.write(f"{utc_time.strftime('%A, %B %d, %Y at %I:%M:%S %p %Z')}")            
        HTML_File.write("</h2>")
        
        HTML_Unit.output_html_footer(HTML_File, TABLES)


def processReport(delete, checkServices, summary, invalid, changed, HTML):
    """
    Process the DeviceList report and generate the reports.
    """

    # Create a CSV reader object
    TABLES = []
    with open("DeviceList.csv", "r", encoding="utf-8") as inputFile:
        reader = csv.reader(inputFile)

        if HTML:
            HTML_File = sys.stdout  # open("DeviceList.html","w")
            HTML_Unit.output_html_header(HTML_File, "Remote.it Account")
            HTML_Unit.output_html_body(HTML_File)

            HTML_File.write("<h2>Created: ")
            utc_time = datetime.datetime.now(datetime.timezone.utc)
            HTML_File.write(f"{utc_time.strftime('%A, %B %d, %Y at %I:%M:%S %p %Z')}")            
            HTML_File.write("</h2>")


        # Skip the header row
        # pylint: disable=W0612
        header = next(reader)

        # Iterate through the rows and count the 'Bulk Service' entries
        ID = None
        devices = {}
        devicesSerial = {}
        last = {}
        created = {}
        problemDevices = defaultdict(int)
        serviceID = {}

        if changed:
            if HTML:
                HTML_Unit.output_table_header(
                    HTML_File,
                    "Changed",
                    "Devices that ID's have changed",
                    [
                        "Original ID",
                        "Created",
                        "Last Contact",
                        "New ID",
                        "Created",
                        "Last Contact",
                    ],
                )
                TABLES.append("Changed")
            else:
                print(
                    "Original ID",
                    "Created",
                    "Last Contact",
                    "New ID",
                    "Created",
                    "Last Contact",
                    sep=", ",
                )

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

            if ID in serviceID:
                serviceID[ID].append(row[0])
            else:
                serviceID[ID] = [row[0]]

            if changed:
                deviceID = row[1]
                if row[3] == "Bulk Service":
                    hyphen_index = deviceID.rfind("-")
                    if hyphen_index != -1:
                        deviceType = deviceID[:hyphen_index]
                        serialNumber = deviceID[hyphen_index + 1 :]
                    else:
                        deviceType = deviceID
                        serialNumber = deviceID

                    #            print("Serial:", deviceType, serialNumber)

                    if serialNumber in devicesSerial:
                        if devicesSerial[serialNumber][0] != deviceType:
                            if row[6] < devicesSerial[serialNumber][1]:
                                if HTML:
                                    HTML_Unit.output_table_row(
                                        HTML_File,
                                        [
                                            deviceID,
                                            row[6],
                                            row[5],
                                            devicesSerial[serialNumber][0],
                                            devicesSerial[serialNumber][1],
                                            devicesSerial[serialNumber][2],
                                        ],
                                    )
                                else:
                                    print(
                                        deviceID,
                                        row[6],
                                        row[5],
                                        devicesSerial[serialNumber][0],
                                        devicesSerial[serialNumber][1],
                                        devicesSerial[serialNumber][2],
                                        sep=", ",
                                    )
                            else:
                                if HTML:
                                    HTML_Unit.output_table_row(
                                        HTML_File,
                                        [
                                            devicesSerial[serialNumber][0],
                                            devicesSerial[serialNumber][1],
                                            devicesSerial[serialNumber][2],
                                            deviceID,
                                            row[6],
                                            row[5],
                                        ],
                                    )
                                else:
                                    print(
                                        devicesSerial[serialNumber][0],
                                        devicesSerial[serialNumber][1],
                                        devicesSerial[serialNumber][2],
                                        deviceID,
                                        row[6],
                                        row[5],
                                        sep=", ",
                                    )
                    else:
                        devicesSerial[serialNumber] = [deviceID, row[6], row[5]]

        #    pprint(devicesSerial)
        #    pprint(created)
        if checkServices and not delete:
            if HTML:
                HTML_Unit.output_table_header(
                    HTML_File,
                    "Services",
                    "Devices with invalid services count",
                    ["Hardware ID", "Device Type", "Device-ID", "Services", "Created"],
                )
                TABLES.append("Services")
            else:
                print("Hardware ID, Device Type, Device-ID, Services, Created")
        # pylint: disable=C0206
        for device in devices:
            #    pprint(device)
            services = len(devices[device])
            deviceID = devices[device][services - 1]

            hyphen_index = deviceID.rfind("-")
            if hyphen_index != -1:
                deviceType = deviceID[:hyphen_index]
                serialNumber = deviceID[hyphen_index + 1 :]
            else:
                deviceType = deviceID
                serialNumber = deviceID

            #        print(deviceType, serialNumber)

            if checkServices or summary:
                #                print (EXPECTED)
                if deviceType in EXPECTED:
                    #                print(devices, services)
                    if not services in EXPECTED[deviceType]:
                        problemDevices[deviceType] += 1
                        if checkServices:
                            if delete:
                                print(
                                    "./RemoteIt-Delete.py --Force @parameters/RemoteIt.Params {} {}".format(
                                        devices[device][services - 1], device
                                    )
                                )
                            else:
                                if HTML:
                                    HTML_Unit.output_table_row(
                                        HTML_File,
                                        [
                                            device,
                                            deviceType,
                                            devices[device][services - 1],
                                            services,
                                            created[device][len(devices[device]) - 1],
                                        ],
                                    )
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
                                        created[device][len(devices[device]) - 1],
                                    )

        if invalid:
            if HTML:
                HTML_Unit.output_table_header(
                    HTML_File,
                    "Invalid",
                    "Devices with invalid services",
                    [
                        "Device",
                        " Device-ID",
                        " Serial",
                        " Web-Valid",
                        " Web-Valid_Create",
                        " Web_No_Serial",
                        " Web_No_Serial_Count",
                        " Web_No_Serial_Create",
                        " Web_No_Serial_ID",
                        " SSH_22 Valid",
                        " SSH_22 Valid_Create",
                        " SSH_22_No_Serial",
                        " SSH_22_No_Serial_Count",
                        " SSH_22_No_Serial_Create",
                        " SSH_22_No_Serial_ID",
                        " Last Contact",
                        " Bulk Created",
                    ],
                )
                TABLES.append("Invalid")
            else:
                print(
                    "Device, Device-ID, Serial, Web-Valid, Web-Valid_Create, Web_No_Serial, Web_No_Serial_Count, Web_No_Serial_Create, Web_No_Serial_ID, SSH_22 Valid, SSH_22 Valid_Create, SSH_22_No_Serial, SSH_22_No_Serial_Count, SSH_22_No_Serial_Create, SSH_22_No_Serial_ID, Last Contact, Bulk Created"
                )

            for device in devices:
                #    pprint(device)
                services = len(devices[device])
                deviceID = devices[device][services - 1]
                hardwareID = serviceID[device][services - 1]
                hyphen_index = deviceID.find("-")
                deviceSerial = deviceID
                if deviceSerial.startswith("EC520-W"):
                    deviceSerial = deviceSerial[8:]
                elif deviceSerial.startswith("EC520"):
                    deviceSerial = deviceSerial[6:]

                if "EC520-_Web_Proxy_80" in devices[device]:
                    if HTML:
                        fields = []
                        fields.append(deviceID)
                        fields.append(hardwareID)
                        fields.append(deviceSerial)
                        fields.append(
                            str(deviceID + "_Web_Proxy_80" in devices[device])
                        )

                        try:
                            fields.append(
                                created[device][
                                    devices[device].index(deviceID + "_Web_Proxy_80")
                                ]
                            )
                        except:
                            fields.append("")

                        fields.append("EC520-_Web_Proxy_80" in devices[device])

                        #                    print("")
                        #                    pprint(devices[device])
                        #                    print("")

                        fields.append(devices[device].count("EC520-_Web_Proxy_80"))
                        fields.append(
                            created[device][
                                devices[device].index("EC520-_Web_Proxy_80")
                            ]
                        )
                        fields.append(
                            serviceID[device][
                                devices[device].index("EC520-_Web_Proxy_80")
                            ]
                        )
                        fields.append(str(deviceID + "_SSH_22" in devices[device]))

                        try:
                            fields.append(
                                created[device][
                                    devices[device].index(deviceID + "_SSH_22")
                                ]
                            )
                        except:
                            fields.append("")

                        try:
                            fields.append(
                                str(
                                    "EC520-_SSH_22"
                                    in devices[device][
                                        devices[device].index(deviceID + "_SSH_22")
                                    ]
                                )
                            )
                        except:
                            fields.append("")

                        fields.append(devices[device].count("EC520-_SSH_22"))

                        try:
                            fields.append(
                                created[device][devices[device].index("EC520-_SSH_22")]
                            )
                        except:
                            fields.append("")

                        fields.append(
                            serviceID[device][devices[device].index("EC520-_SSH_22")]
                        )
                        fields.append(last[device])
                        fields.append(created[device][len(devices[device]) - 1])
                        HTML_Unit.output_table_row(HTML_File, fields)

                    else:
                        print(deviceID, end="")
                        print(" , ", hardwareID, end="")
                        print(" , ", deviceSerial, end="")
                        print(
                            " , ",
                            str(deviceID + "_Web_Proxy_80" in devices[device]),
                            end="",
                        )
                        try:
                            print(
                                " , ",
                                created[device][
                                    devices[device].index(deviceID + "_Web_Proxy_80")
                                ],
                                end="",
                            )
                        except:
                            print(" , ", end="")

                        print(" , ", "EC520-_Web_Proxy_80" in devices[device], end="")

                        #                    print("")
                        #                    pprint(devices[device])
                        #                    print("")

                        print(
                            " , ", devices[device].count("EC520-_Web_Proxy_80"), end=""
                        )
                        print(
                            " , ",
                            created[device][
                                devices[device].index("EC520-_Web_Proxy_80")
                            ],
                            end="",
                        )
                        print(
                            " , ",
                            serviceID[device][
                                devices[device].index("EC520-_Web_Proxy_80")
                            ],
                            end="",
                        )

                        print(
                            " , ", str(deviceID + "_SSH_22" in devices[device]), end=""
                        )

                        try:
                            print(
                                " , ",
                                created[device][
                                    devices[device].index(deviceID + "_SSH_22")
                                ],
                                end="",
                            )
                        except:
                            print(" , ", end="")

                        try:
                            print(
                                " , ",
                                str(
                                    "EC520-_SSH_22"
                                    in devices[device][
                                        devices[device].index(deviceID + "_SSH_22")
                                    ]
                                ),
                                end="",
                            )
                        except:
                            print(" , ", end="")

                        print(" , ", devices[device].count("EC520-_SSH_22"), end="")

                        try:
                            print(
                                " , ",
                                created[device][devices[device].index("EC520-_SSH_22")],
                                end="",
                            )
                        except:
                            print(" , ", end="")

                        print(
                            " , ",
                            serviceID[device][devices[device].index("EC520-_SSH_22")],
                            end="",
                        )
                        print(" , ", last[device], end="")
                        print(" , ", created[device][len(devices[device]) - 1])

        #    , str(len(device)))
        #    pprint(problemDevices)

        if summary:
            for device, total in problemDevices.items():
                print(f"{device}: {total}")
        #    pprint(problemDevices)
        # Print the count
        # print("Number of 'Bulk Service' devices:", bulk_service_count)
        if HTML:
            if changed or checkServices or invalid:
                HTML_Unit.output_table_footer(HTML_File)

            HTML_File.write("<h2>Completed: ")
            utc_time = datetime.datetime.now(datetime.timezone.utc)
            HTML_File.write(f"{utc_time.strftime('%A, %B %d, %Y at %I:%M:%S %p %Z')}")            
            HTML_File.write("</h2>")

            HTML_Unit.output_html_footer(HTML_File, TABLES)


def main():
    """
    Main Processing
    """
    global EXPECTED
    args = get_args()
    if args["SNM941"]:
        EXPECTED = {"EC520": [3], "SNM941": [11, 12], "Tablet": [2]}
    #        EXPECTED = {"EC520": [3], "SNM941": [11], "Tablet": [2]}
    else:
        EXPECTED = {"EC520": [3], "Tablet": [2]}

    if args["Details"] or args["Devices"]:
        FullReport(args["Details"])
    else:
        processReport(
            args["Delete"],
            args["Services"],
            args["Summary"],
            args["Invalid"],
            args["Changed"],
            args["HTML"],
        )


if __name__ == "__main__":
    main()
