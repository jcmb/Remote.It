#!/usr/bin/env python3
import requests


import logging

import json
from pprint import pprint

from datetime import datetime

try:
    import http.client as http_client
except ImportError:
    # Python 2, not tested any longer
    import httplib as http_client



class RemoteIt-Graph(object):
   def __init__(self, key_id,key_secret_id, logging_dir=None, timeout=5, host="api.remote.it", url_path="/graphql/v1",verbose=False):
      self.host=host
      self.url=url
      self.timeout=timeout
      self.log_dir=logging_dir
      self.verbose=verbose
      self.reason=None

      if self.verbose:
         logging.getLogger("requests").setLevel(logging.DEBUG)
         http_client.HTTPConnection.debuglevel = 1
      else:
         logging.getLogger("requests").setLevel(logging.WARNING)



   def set_logging(self,logging_dir):
      self.log_dir=logging_dir


   def log_reply(self,model,reply):
      if self.log_dir == None:
         return

      log_file_dir=self.log_dir+"/"+model
      log_file_name=log_file_dir+"/"+datetime.now().strftime("%Y-%m-%d--%H-%M-%S")+".json"
      if not os.path.exists(log_file_dir):
         os.makedirs(log_file_dir)

      log=open(log_file_name,"w")
      log.write(reply)
      log.close()


