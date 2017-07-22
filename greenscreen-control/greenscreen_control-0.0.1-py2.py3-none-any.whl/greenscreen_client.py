#!/usr/bin/python

import json
import logging
import requests

class GreenScreenClient(object):
  def __init__(self, server):
    if not server.startswith("http://") and not server.startswith("https://"):
      self._server = "http://" + server
    else:
      self._server = server

  def _check_response(self, response):
    if response.status_code != requests.codes.ok:
      logging.error(
          "Unexpected status code (%i) from: %s" % (
          response.status_code, response.url))
      return False
    return True

  def _decode_json(self, response):
    try:
      data = response.json()
    except ValueError:
      logging.exception(
          "Could not decode JSON: %s" % response.url)
      return None
    return data

  def _send_get_json_request(self, endpoint):
    url = '%s/%s' % (self._server, endpoint)
    try:
      response = requests.get(url)
    except:
      logging.exception("Failure during GET request: %s" % url)
      return None

    if self._check_response(response):
      return self._decode_json(response)
    return None

  def _send_put_json_request(self, endpoint, data):
    url = '%s/%s' % (self._server, endpoint)
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    try:
      response = requests.put(url, data=json.dumps(data), headers=headers);
    except:
      logging.exception("Failure during PUT request: %s" % url)
      return None

    return self._check_response(response)

  def get_receivers(self):
    return self._send_get_json_request("api/receivers")

  def set_receiver(self, id, data):
    return self._send_put_json_request("api/receivers/%s" % id, data)

  def get_channels(self):
    return self._send_get_json_request("api/channels")
  
  def get_channel_id(self, channel_name):
    channels = self.get_channels()  
    if not channels:
      return None
    for i in range(len(channels)):
      if channels[i]["name"] == channel_name:
        return channels[i]["id"]

    logging.error("Could not find channel with name: %s" % channel_name)
    return None
 
  def set_channel_for_chromecast(self, chromecast_name, target_channel_name):
    target_channel_id = self.get_channel_id(target_channel_name)
    if not target_channel_id:
      return False

    chromecasts = self.get_receivers()
    if not chromecasts:
      return False

    for chromecast in chromecasts:
      if chromecast["name"] == chromecast_name:
        chromecast["channelId"] = target_channel_id
        logging.info("Setting channel for '%s' to '%s'" % (
            chromecast_name, target_channel_name))
        # Reset alerts.
        chromecast["alert"] = None
        self.set_receiver(chromecast['id'], chromecast)
        break
    else:
      logging.error("Could not find a chromecast with name: %s", chromecast_name)
      return False
