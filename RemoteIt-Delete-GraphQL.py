#!/usr/bin/env python3
import argparse
import sys
import requests

from base64 import b64decode

try:
    from requests_http_signature import HTTPSignatureAuth
except:
    sys.exit("HTTPSignatureAuth is not installed. Install it using pip3 install requests_http_signature==v0.1.0")


# cgitb.enable()
# from JCMBSoftPyLib import HTML_Unit

from pprint import pprint

import csv

import os


def get_args():

    parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@", description="Remote.It Account Summary."
    )

    parser.add_argument(
        "key_id",
        help="Account Key",
    )
    parser.add_argument(
        "key_secret_id",
        help="Account Secret ID",
    )

    parser.add_argument("Device_ID", help="Device ID, <Model>-<Serial>")
    parser.add_argument("HW_ID", help="Hardware ID", nargs="?")
    parser.add_argument("--Tell", help="Tell Settings", action="store_true")
    parser.add_argument(
        "--Force",
        help="Force Deletion, even if it is the only copy of the device in the account",
        action="store_true",
    )
    parser.add_argument(
        "--DryRun",
        help="Do not delete, just show what would happen",
        action="store_true",
    )
    parser.add_argument("--Verbose", help="Verbose", action="store_true")

    parser = parser.parse_args()
    args = {}
    args["key_id"] = parser.key_id
    args["key_secret_id"] = parser.key_secret_id
    args["Device_ID"] = parser.Device_ID
    args["HW_ID"] = parser.HW_ID
    args["Force"] = parser.Force
    args["DryRun"] = parser.DryRun
    args["Verbose"] = parser.Verbose
    #   args["HW_ID"]=args["HW_ID"].replace(":","")

    if parser.Tell:
        sys.stderr.write("key_id: {}\n".format(args["key_id"]))
        sys.stderr.write("key_secret_id: {}\n".format(args["key_secret_id"]))
        sys.stderr.write("Device ID : {}\n".format(args["Device_ID"]))
        sys.stderr.write("HW ID : {}\n".format(args["HW_ID"]))
        sys.stderr.write("Force Delete: {}\n".format(args["Force"]))
        sys.stderr.write("DryRun: {}\n".format(args["DryRun"]))
        sys.stderr.write("Verbose: {}\n".format(args["Verbose"]))

    return args

def delete_device(
    key_id, key_secret_id, Device_ID, HW_ID, Force=True, DryRun=False, Verbose=False
):

    host = "api.remote.it"
    url_path = "/graphql/v1"
    content_type_header = "application/json"

    if Verbose:
        sys.stderr.write("Geting Device information for {}.\n".format(Device_ID))

    mutation = 'mutation {deleteDevice( deviceId: "' + HW_ID + '" )}'

    body = {
        "query": mutation
        }


    if Verbose:
        print(body,file=sys.stderr)

    content_length_header = str(len(body))
    headers = {
        "host": host,
        "path": url_path,
        "content-type": content_type_header,
        "content-length": content_length_header,
    }

    response = requests.post(
        "https://" + host + url_path,
        json=body,
        auth=HTTPSignatureAuth(
            algorithm="hmac-sha256",
            key=b64decode(key_secret_id),
            key_id=key_id,
            headers=[
                "(request-target)",
                "host",
                "date",
                "content-type",
                "content-length",
            ],
        ),
        headers=headers,
    )
    #        print(data.decode('utf-8'))
    if response.status_code != 200:
        sys.stderr.write("Error in Request\n")
        sys.stderr.write(response.text)
        sys.exit(3)


    if Verbose:
        print(response.json())

    reply = response.json()


def main():
    args = get_args()

    if os.path.isfile(args["Device_ID"]):
        if args["Verbose"]:
            sys.stdout.write("Using CSV file: {}\n".format(args["Device_ID"]))

        with open(args["Device_ID"], "r") as file:
            reader = csv.reader(file)
            header = next(reader)
            #         print(header)
            if header != [
                "id",
                "name",
                "hardwareId",
                "title",
                "state",
                "timestamp",
                "created",
                "address",
            ]:
                sys.exit(
                    "CSV file not of the correct format. Should have fields 'id', 'name', 'hardwareId', 'title', 'state', 'timestamp', 'created', 'address'"
                )

            for row in reader:
                delete_device(
                    args["key_id"],
                    args["key_secret_id"],
                    row[1],
                    row[0],
                    args["Force"],
                    args["DryRun"],
                    args["Verbose"],
                )

    else:
        if args["HW_ID"] == None:
            sys.exit("HW Must be provided when deleting a single value")
        delete_device(
            args["key_id"],
            args["key_secret_id"],
            args["Device_ID"],
            args["HW_ID"],
            args["Force"],
            args["DryRun"],
            args["Verbose"],
        )


#   pprint(remotes)

if __name__ == "__main__":
    main()
