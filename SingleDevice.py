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


try:
    from requests_http_signature import HTTPSignatureAuth
except:
    sys.exit("HTTPSignatureAuth is not installed. Install it using pip3 install requests_http_signature==v0.1.0")

import http.client as http_client
from requests_toolbelt.utils import dump

#logging.basicConfig(level=logging.DEBUG)

# Enable requests logging
#http_client_logger = logging.getLogger('urllib3')
#http_client_logger.setLevel(logging.DEBUG)
#http_client_logger.propagate = True


def get_args():

   parser = argparse.ArgumentParser(fromfile_prefix_chars="@",description='Remote.It Single Device.')

   parser.add_argument("key_id", help="Account Key",)
   parser.add_argument("key_secret_id", help="Account Secret ID",)
   parser.add_argument("Device_ID", help="Device ID")
   parser.add_argument("--Tell", "-T", help="Tell Settings",action="store_true")
   parser.add_argument("--Verbose","-v", help="Verbose",action="store_true")
   parser = parser.parse_args()
   return (vars(parser))



def SingleDevice(key_id,key_secret_id,Device_ID,size=800):
    host = 'api.remote.it'
    url_path = '/graphql/v1'
    content_type_header = 'application/json'

    hasMore=True
    last=""
    items_so_far=0
    print("Name", "Enabled","ID", "Owner", "Created", "LastReported","Services","eMail","InternalIPType","InternalIP","ExternalIP",sep=',')

    while hasMore:

    #    body = {"query": "query { login { devices (size : 10, after : \"" + last + "\" sort: \"created\") { hasMore total  last items { id  name owner { email } created lastReported}}}}"}
        body = {"query": "query { login { devices (size : " + str(size) + " after : \"" + last + "\" sort: \"created\") { hasMore total  last items { enabled platform id  name owner { email } created lastReported services {title  enabled state name} endpoint {name internalAddress externalAddress}}}}}"}
        body = {"query": "query { login { devices (size : " + str(size) + " after : \"" + last + "\" sort: \"created\") { hasMore total  last items { enabled platform id  name owner { email } created lastReported services {title  enabled state name} endpoint {name internalAddress externalAddress}}}}}"}
        body = {"query": 'query getDevices($size: Int, $from: Int, $sort: String, $state: String, $name: String) ' +
                   '{ login ' +
                      '{ devices(size: $size , from: $from, sort: $sort, state: $state, name: $name) '+
                          '{ total hasMore' +
                              '  items { id name hardwareId created ' +
                                 ' services{ id name } '+
#                                 ' endpoint {name internalAddress externalAddress} ' +
                              '} '+
                          '}' +
                       '}' +
                    '} ' +
                   ' #Variables { "size": 10, "from": 0,  "sort": "name", "state": "inactive", "name": "SNM941-6440764199" '}

        query = '''
query getDevices($size: Int, $from: Int, $sort: String, $state: String, $name: String) {
  login {
    devices(size: $size, from: $from, sort: $sort, state: $state, name: $name) {
      total
      hasMore
      last
      items {
        enabled
        platform
        id
        name
        hardwareId
        created
        lastReported
        services {
          id
          name
        }
        endpoint {
           name
           internalAddress
           externalAddress}
      }
    }
  }
}'''

        variables = {
            "size": 100,
            "from": 0,
            "sort": "name",
            "state": "inactive",
            "name": "EC520-0049J023YU"
        }

# Create the request payload
        body = {
            "query": query,
            "variables": variables
        }

#        print(body,file=sys.stderr)
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
        data = dump.dump_all(response)
#        print(data.decode('utf-8'))
        if response.status_code != 200:
            sys.stderr.write("Error in Request\n")
            sys.stderr.write(response.text)
            sys.exit(3)

        reply=response.json()
#        pprint(reply)
        pprint(len(response.json()["data"] ["login"] ["devices"]["items"]))
#        with open("DeviceList.txt", "w") as f:
#            f.write(response.text)

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

        SNMSubnet=ipaddress.ip_network("192.168.88.0/24")
        VerizonSubnet=ipaddress.ip_network("100.0.0.0/8")
#        NMSubnet=ipaddress.ip_network("192.168.9.0/24")

        for device in RemoteItJson["items"]:
#            pprint(device)
#            pprint(device["services"])

            has_VNC_service=False

            for service in device["services"]:
                if service["name"] == "VNC":
                    has_VNC_service=True
#                    has_VNC_service=True



            if device["endpoint"] == None:
               internalAddress=None
               externalAddress=None
               internalAddressStr=""
               internalAddressType=""
            else:
               try:
                   internalAddress=device["endpoint"]["internalAddress"]
                   internalAddressStr=internalAddress[:internalAddress.index(":")]
                   internalAddressType=""
               except:
                   internalAddress=None
                   internalAddressStr=""
                   internalAddressType=""

               try:
                   externalAddress=device["endpoint"]["externalAddress"]
               except:
                   externalAddress=None

#               print (device["endpoint"]["name"])

            if internalAddress != None:
                internalAddressStr=internalAddress[:internalAddress.index(":")]
#                print(internalAddressStr)
                internalIP=ipaddress.ip_address(internalAddressStr)
                internalIP=ipaddress.IPv4Network(internalAddressStr)

                internalAddressType="Normal"

                if internalIP.subnet_of(SNMSubnet):
                    internalAddressType="SNM"
                elif internalIP.subnet_of(VerizonSubnet):
                    internalAddressType="Verizon"
                else:
                    if internalIP.is_private:
                        internalAddressType="Private"
            try:
                eMail=device["owner"]["email"]
            except:
                eMail="None"

#            print(internalAddressStr)
            print(device["name"],device["enabled"],device["id"],eMail,device["created"],device["lastReported"],len(device["services"]),eMail,internalAddressType,internalAddressStr,externalAddress,sep=',')
    #        if device["owner"]["email"].lower() != "civil-remot3it-provisioning-ug@trimble.com":
    #            print(device["name"],device["id"],device["owner"]["email"],device["created"],sep=',')
    #            invalid_emails+=1
        sys.stderr.write("{} of {}\n".format(items_so_far,RemoteItJson["total"]))

        hasMore=RemoteItJson["hasMore"]
        last=RemoteItJson["last"]

def main():
   args=get_args()
   if args["Verbose"]:
       http_client.HTTPConnection.debuglevel = 1
   if args["Tell"]:
       sys.stderr.write("Key_Id: {}\n".format(args["key_id"]))
       sys.stderr.write("Key Secret: {}\n".format(args["key_secret_id"]))


   SingleDevice(args["key_id"],args["key_secret_id"],args["Device_ID"])


if __name__ == '__main__':
    main()

#pprint(invalid_emails)
