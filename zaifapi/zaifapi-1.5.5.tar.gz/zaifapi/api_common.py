import json
import requests
from abc import ABCMeta


def get_response(url, params=None, headers=None):
    response = requests.post(url, data=params, headers=headers)
    if response.status_code != 200:
        raise Exception('return status code is {}'.format(response.status_code))
    return json.loads(response.text)


class AbsZaifBaseApi(object):
    __metaclass__ = ABCMeta
    _use_https = True

    def get_protocol(self):
        if self._use_https:
            return 'https'
        return 'http'
