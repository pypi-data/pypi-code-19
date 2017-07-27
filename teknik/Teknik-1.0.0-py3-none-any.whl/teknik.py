# Copyright (c) 2017 by Uncled1023 <admin@teknik.io>
#
# License BSD 3-Clause

MODULE_NAME = "Teknik Services"
MODULE_AUTHOR = "Uncled1023"
MODULE_VERSION = "0.1"
MODULE_LICENSE = "BSD 3-Clause"

import_success = True

defaultUrl = 'https://api.teknik.io/v1/'
defaultUsername = ''
defaultToken = ''

# Base Libraries
import base64
import json
import urlparse

# Dependencies
try:
  import requests
except ImportError, message:
  print('Missing package(s) for %s: %s' % (MODULE_NAME, message))
  import_success = False
  
# Main Functions
def UploadFile(url, filePath, username, authToken):  
  files = {'file': open(filePath, "rb")}
  
  if url is None:
    url = defaultUrl
  
  if username is None:
    username = defaultUsername
  
  if authToken is None:
    authToken = defaultToken
  
  # Create a header if they have added auth info
  headers = {}
  if username != '' and authToken != '':
    encAuth = base64.b64encode(username + ':' + authToken)
    headers = {'Authorization': 'Basic ' + encAuth}
  
  r = requests.post(GetUrl(url, 'upload'), files=files, headers=headers)
  jObj = json.loads(r.text)
  
  return jObj

def GetAPIUrl(url, service):
  finalUrl = ''
  
  if url is None or url == '':
    url = defaultUrl

  server = service.lower()
  if service == 'upload':
    finalUrl = urlparse.urljoin(url, 'Upload')
  elif service == 'paste':
    finalUrl = urlparse.urljoin(url, 'Paste')
  
  return finalUrl
  
# Entry Point
if __name__ == "__main__" and import_success:
  # do work?