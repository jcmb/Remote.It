#!/usr/bin/env python3
import os
import requests
import json
from base64 import b64decode
from pprint import pprint
import sys
import logging
import argparse
import ipaddress
import cgitb
import urllib.parse


try:
    from requests_http_signature import HTTPSignatureAuth
except:
    sys.exit("HTTPSignatureAuth is not installed. Install it using pip3 install requests_http_signature==v0.1.0")

import http.client as http_client

try:
   from JCMBSoftPyLib import HTML_Unit
   HTML_Available=True
except:
   HTML_Available=False


def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It ScreenView Summary.')

   parser.add_argument("key_id", help="Account Key",)
   parser.add_argument("key_secret_id", help="Account Secret ID",)
   parser.add_argument("--Tell", "-T", help="Tell Settings",action="store_true")
   parser.add_argument("--Verbose","-v", help="Verbose",action="store_true")
   parser.add_argument("--html", help="Output_in_HTML",action="store_true")
   parser = parser.parse_args()
   return (vars(parser))



def Full_Account(key_id,key_secret_id,HTML,size=1000):
    host = 'api.remote.it'
    url_path = '/graphql/v1'
    content_type_header = 'application/json'

    hasMore=True
    last=""
    items_so_far=0
    if HTML:
       HTML_Unit.output_html_header(sys.stdout,"Sync Details for Trimble HH")
       HTML_Unit.output_table_header(sys.stdout,"ScreenView","Remote Access",["Name", "Active","Device ID", "Created", "LastReported","Services","Screen_Service","Enabled"],100)
    else:
        print("Name", "Active","Device ID", "Created", "LastReported","Services","Screen_Service","Enabled",sep=',')

    while hasMore:

    #    body = {"query": "query { login { devices (size : 10, after : \"" + last + "\" sort: \"created\") { hasMore total  last items { id  name owner { email } created lastReported}}}}"}
        body = {"query": "query { login { devices (size : " + str(size) + " after : \"" + last + "\" sort: \"created\") { hasMore total  last items { enabled platform id  name owner { email } created lastReported services {id title  enabled state name} endpoint {name internalAddress externalAddress}}}}}"}
#        body= {"query" :  "query { login { report(name: \"DeviceList\")}}"}
        content_length_header = str(len(body))
        headers = {
            'host': host,
            'path': url_path,
            'content-type': content_type_header,
            'content-length': content_length_header,
        }

        response = requests.post('https://' + host + url_path,
                                 json=body,
                                 auth=HTTPSignatureAuth(algorithm="hmac-sha256",
                                                        key=b64decode(key_secret_id),
                                                        key_id=key_id,
                                                        headers=[
                                                            '(request-target)', 'host',
                                                            'date', 'content-type',
                                                            'content-length'
                                                        ]),
                                 headers=headers)

        if response.status_code != 200:
            sys.stderr.write("Error in Request\n")
            sys.stderr.write(response.text)
            sys.exit(3)

        reply=response.json()
#        with open("DeviceList.txt", "w") as f:
#            f.write(response.text)
#        pprint(reply)

        if "errors" in reply:
            sys.stderr.write("Error in Query\n")
            sys.stderr.write(reply)
            sys.exit(2)

        RemoteItJson=response.json()["data"] ["login"] ["devices"]
        if response.status_code != 200:
            print(response.status_code)
            sys.exit(1)

        invalid_emails=0

        items_so_far+=len(RemoteItJson["items"])

        for device in RemoteItJson["items"]:
#            pprint(device)
#            pprint(device["services"])

            has_Screen_service=False
            active=False

            for service in device["services"]:
                if service["title"] == "Screen View":
                    has_Screen_service=True
                    active=service["state"] == 'active'
                    service_id=service["id"]
#                    has_VNC_service=True


#            print(internalAddressStr)
            if HTML:
               if active:
                   HTML_Unit.output_table_row(sys.stdout, [
                           '<a href="/cgi-bin/remote_screen_connect?Address={}&IP=0.0.0.0">{}</a>'.format(urllib.parse.quote(service_id), device["name"]),
                   active,
                   device["id"],
                   device["created"],device["lastReported"],len(device["services"]),has_Screen_service,device["enabled"]])
               else:
                   HTML_Unit.output_table_row(sys.stdout, [device["name"],active,device["id"],device["created"],device["lastReported"],len(device["services"]),has_Screen_service,device["enabled"]])
            else:
                print(device["name"],active, device["id"],device["created"],device["lastReported"],len(device["services"]),has_Screen_service,device["enabled"],sep=',')
    #        if device["owner"]["email"].lower() != "civil-remot3it-provisioning-ug@trimble.com":
    #            print(device["name"],device["id"],device["owner"]["email"],device["created"],sep=',')
    #            invalid_emails+=1
        if not HTML:
            sys.stderr.write("{} of {}\n".format(items_so_far,RemoteItJson["total"]))

        hasMore=RemoteItJson["hasMore"]
        last=RemoteItJson["last"]

    if HTML:
       HTML_Unit.output_table_footer(sys.stdout)
       HTML_Unit.output_html_footer(sys.stdout,["ScreenView"])


def main(HTML_Available):
   args=get_args()

   if args["html"] and not HTML_Available:
       sys.exit("HTML Format requested and the HTML_Unit from JCMBSoftPyLib is not available")


   if args["Verbose"]:
       http_client.HTTPConnection.debuglevel = 1
   if args["Tell"]:
       sys.stderr.write("Key_Id: {}\n".format(args["key_id"]))
       sys.stderr.write("Key Secret: {}\n".format(args["key_secret_id"]))


   Full_Account(args["key_id"],args["key_secret_id"],args["html"],size=800)


if __name__ == '__main__':
    main(HTML_Available)

#pprint(invalid_emails)
