#!/usr/bin/env python3
import argparse
import os
import sys
import tempfile
import time
from base64 import b64decode

import http.client as http_client
import requests

try:
    from requests_http_signature import HTTPSignatureAuth
except ImportError:
    sys.exit(
        "HTTPSignatureAuth is not installed. Install it using "
        "pip3 install requests-http-signature==0.1.0"
    )


def get_args():
    parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@", description="Remote.It Account Summary."
    )
    parser.add_argument("key_id", help="Account Key")
    parser.add_argument("key_secret_id", help="Account Secret ID")
    parser.add_argument("--Tell", "-T", help="Tell Settings", action="store_true")
    parser.add_argument("--Verbose", "-v", help="Verbose", action="store_true")
    return vars(parser.parse_args())


def Full_Account_Report(key_id, key_secret_id, size=1000):
    host = "api.remote.it"
    url_path = "/graphql/v1"
    content_type_header = "application/json"

    body = {"query": 'query { login { report(name: "DeviceList")}}'}
    content_length_header = str(len(body))
    headers = {
        "host": host,
        "path": url_path,
        "content-type": content_type_header,
        "content-length": content_length_header,
    }

    downloaded = False
    attempt_count = 1
    while not downloaded:
        start_time = time.time()
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
            timeout=120,
        )

        if response.status_code != 200:
            elapsed_time = time.time() - start_time
            sys.stderr.write("Error in Request. Try: {}\n".format(attempt_count))
            sys.stderr.write("Elapsed time: {:.2f} seconds\n".format(elapsed_time))
            sys.stderr.write(response.text)
            attempt_count += 1
            if attempt_count < 5:
                sys.stderr.write("\nRetry in 10 seconds\n")
            else:
                sys.exit("Aborting")
            sys.stderr.flush()
            time.sleep(10)
        else:
            downloaded = True

    reply = response.json()
    download_url = reply["data"]["login"]["report"]
    print("Downloading report from: {}".format(download_url))
    response = requests.get(download_url, timeout=300)
    response.raise_for_status()
    print("Report downloaded.")

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, dir=".", prefix="DeviceList.", suffix=".tmp"
    ) as tmp_file:
        tmp_file.write(response.text)
        tmp_path = tmp_file.name

    os.replace(tmp_path, "DeviceList.csv")


def main():
    args = get_args()
    if args["Verbose"]:
        http_client.HTTPConnection.debuglevel = 1
    if args["Tell"]:
        sys.stderr.write("Key_Id: {}\n".format(args["key_id"]))
        sys.stderr.write("Key Secret: {}\n".format(args["key_secret_id"]))

    Full_Account_Report(args["key_id"], args["key_secret_id"], size=800)


if __name__ == "__main__":
    main()
