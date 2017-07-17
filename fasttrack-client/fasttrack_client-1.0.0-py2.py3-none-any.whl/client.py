try:
  from httplib import HTTPSConnection
except Exception as e:
  from http.client import HTTPSConnection

try:
  from urllib import urlencode
except Exception as e:
  from urllib.parse import urlencode

import json

from .constants import ACCEPT, VERSION, PATHNAME_COMPANY, PATHNAME_CONTACT, URL
from .common import exceptionForResponse

class Client:
  def __init__(self, token):
    self.token = token

  # Request to the API endpoint
  def get(self, path, params):
    headers = {
      'Authorization' : 'Token ' + self.token,
      'Accept'        : ACCEPT + '; version = ' + str(VERSION)
    }

    params = urlencode(params)

    conn = HTTPSConnection(URL)
    conn.request('GET', path + '?' + params, None, headers)

    response = conn.getresponse()

    data = json.loads(response.read())

    if response.status != 200:
        FastTrackException = exceptionForResponse(response.status, getattr(data, 'error_code', None))

        if (FastTrackException != None):
          raise FastTrackException(getattr(data, 'detail', None))

    return data

  # Retrieve company details with a `domain`
  def getCompany(self, domain):
    return self.get(PATHNAME_COMPANY, {
      'domain' : domain
    })

  # Retrieve contact details with an `email`
  def getContact(self, email):
    return self.get(PATHNAME_CONTACT, {
      'email' : email
    })
