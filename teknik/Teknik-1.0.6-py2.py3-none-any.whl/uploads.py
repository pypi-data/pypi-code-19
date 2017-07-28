# Copyright (c) 2017 by Uncled1023 <admin@teknik.io>
#
# License BSD 3-Clause

# Base Libraries
import base64
import json

# Local Libraries
from . import util

# Dependencies
import requests

# Main Functions
def UploadFile(url, filePath, username, authToken):  
  files = {'file': open(filePath, "rb")}
  
  if url is None:
    url = util.defaultUrl
  
  if username is None:
    username = util.defaultUsername
  
  if authToken is None:
    authToken = util.defaultToken
  
  # Create a header if they have added auth info
  headers = {}
  if username != '' and authToken != '':
    encAuth = base64.b64encode(username + ':' + authToken)
    headers = {'Authorization': 'Basic ' + encAuth}
  
  r = requests.post(util.GetUrl(url, 'upload'), files=files, headers=headers)
  jObj = json.loads(r.text)
  
  return jObj