"""
    COPYRIGHT (C) 2017 by Sebastian Stigler

    NAME
        server.py -- Component which sends the result to the logging server

    FIRST RELEASE
        2017-07-05  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""
import json
import logging

import requests

from messgeraet_anzapfen.configurable import Configurable

_logger = logging.getLogger(__name__)

__all__ = ['Server', 'ServerError']


class ServerError(Exception):
    """Problems while sending"""


class Server(Configurable):
    """Sends the result to the logging server"""

    config_keys = ['url', 'endpoint', 'status_code', 'sensor_id']

    def send(self, data, sending):
        """send data to the logging server"""
        url = self.config.get('url')
        url += self.config.get('endpoint')
        send_data = {'sensor': self.config.get('sensor_id'),
                     'value': data}
        if sending:
            _logger.info('Sending data from sensor %s to %s.' %
                         (self.config.get('sensor_id'), url))
            try:
                res = requests.post(url, json=send_data)
                res.raise_for_status()
                _logger.info("Post of sensor data successfully.")
                _logger.debug("Result text of postrequest: %s" % res.text)
            except requests.exceptions.RequestException as err:
                _logger.error('Requests error: {err}'.format(err=err))
        else:
            print(json.dumps(send_data, indent=2))

# vim: ft=python ts=4 sta sw=4 et ai
# python: 3
