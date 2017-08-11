#!/usr/bin/env python

from future.standard_library import install_aliases
install_aliases()


import json
import jwt
import requests
import time
import os
import base64

import sys
# if sys.version_info < (3, 0):
#     raise "must use python 2.5 or greater"

use_environment_variables = None

try:
    from django.conf import settings
except ImportError:
    use_environment_variables = True


class BrightRollClient:
  client_id = None
  client_secret = None
  id_host = None
  dsp_host = None
  request_auth_url = None
  yahoo_auth = None
  raw_token_results = None
  token = None


  def __init__(self):
    self.client_id = os.environ['BR_CLIENT_ID']
    self.client_secret = os.environ['BR_CLIENT_SECRET']
    self.id_host = os.environ['BR_ID_HOST']
    self.dsp_host = os.environ['BR_DSP_HOST']
    self.request_auth_url = self.id_host + "/oauth2/request_auth?client_id=" + self.client_id + "&redirect_uri=oob&response_type=code&language=en-us"

  def get_yahoo_auth_url(self):
    print("Go to this URL:")
    print(self.request_auth_url)

  def set_yahoo_auth(self, s_auth):
    self.yahoo_auth = s_auth
    return self.yahoo_auth

  def base64auth(self):
    return base64.b64encode((self.client_id + ":" + self.client_secret).encode())
    
  def get_access_token_json(self):
    get_token_url = self.id_host + "/oauth2/get_token"
    # payload = {'grant_type':'authorization_code', 'redirect_uri':'oob','code':self.yahoo_auth}
    payload = "grant_type=authorization_code&redirect_uri=oob&code=" + self.yahoo_auth
    # headers = {'Content-Type': 'application/json', 'Authorization': "Basic " + self.base64auth()}
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': "Basic " + self.base64auth().decode('utf-8')}
    print(get_token_url)
    print(payload)
    print(headers)
    # r = requests.post(get_token_url, json=payload, headers=headers)
    r = requests.post(get_token_url, data=payload, headers=headers)
    results_json = r.json()
    return results_json

  def refresh_access_token(self):
    get_token_url = self.id_host + "/oauth2/get_token"
    payload = "grant_type=refresh_token&redirect_uri=oob&refresh_token=" + self.raw_token_results['refresh_token'].encode('utf-8')
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': "Basic " + self.base64auth().decode('utf-8')}
    r = requests.post(get_token_url, data=payload, headers=headers)
    results_json = r.json()
    self.raw_token_results = r.json()
    return results_json

  def cli_auth_dance(self):
    self.get_yahoo_auth_url()
    if sys.version_info < (3, 0):
      self.yahoo_auth = raw_input("Enter Yahoo! auth code: ")
    else:
      self.yahoo_auth = input("Enter Yahoo! auth code: ")

    print("Auth code, {}, entered.".format(self.yahoo_auth))
    self.raw_token_results = self.get_access_token_json()
    print("raw_token_results:")
    print(self.raw_token_results)

  #
  #
  # traffic types
  #
  #
  def traffic_types(self, s_type):
    headers = {'Content-Type': 'application/json', 'X-Auth-Method': 'OAUTH', 'X-Auth-Token': str(self.raw_token_results['access_token'])}
    results = requests.get(self.dsp_host + "/traffic/" + str(s_type)  , headers=headers)
    types = results.json()
    return types

  def traffic_type_by_id(self, s_type, cid):
    headers = {'Content-Type': 'application/json', 'X-Auth-Method': 'OAUTH', 'X-Auth-Token': str(self.raw_token_results['access_token'])}
    result = requests.get(self.dsp_host + "/traffic/" + str(s_type)  + "/" + str(cid), headers=headers)
    traffic_type = result.json()
    return traffic_type
  
  def traffic_types_by_filter(self, s_type, account_id, page, limit, sort, direction, query):
    headers = {'Content-Type': 'application/json', 'X-Auth-Method': 'OAUTH', 'X-Auth-Token': str(self.raw_token_results['access_token'])}
    results = requests.get(self.dsp_host + "/traffic/" + str(s_type) + "?accountId=" + str(account_id) + "&page=" + str(page) + "&limit=" + str(limit) + "&sort=" + str(sort) + "&dir=" + str(direction) + "&query=" + str(query), headers=headers)
    traffic_types = results.json()
    return traffic_types
    
  def update_traffic_type(self, s_type, cid, payload):
    headers = {'Content-Type': 'application/json', 'X-Auth-Method': 'OAUTH', 'X-Auth-Token': str(self.raw_token_results['access_token'])}
    r = requests.put(self.dsp_host + "/traffic/" + str(s_type) + "/" + str(cid), data=payload, headers=headers)
    return r

  def create_traffic_type(self, s_type, payload):
    headers = {'Content-Type': 'application/json', 'X-Auth-Method': 'OAUTH', 'X-Auth-Token': str(self.raw_token_results['access_token'])}
    r = requests.post(self.dsp_host + "/traffic/" + str(s_type) , data=payload, headers=headers)
    return r

