import requests

from registryctl.common.exceptions import *

REGISTRY_HEADER_V2 = 'application/vnd.docker.distribution.manifest.v2+json'

class BaseClient(object):
    def __init__(self, url, auth=None, commands=None):
        self._url = url
        self._session = requests.Session()
        self._basic_auth = auth
        self._header_v2 = {'Accept': REGISTRY_HEADER_V2}

    def _get(self, url):
        return self._session.get(url=url,auth=self._basic_auth)

    def _head(self, url, header):
        req_head = self._session.head(url=url,
                                      auth=self._basic_auth,
                                      headers=self._header_v2)
        if req_head.status_code == 404:
            raise NotFoundException()
        return req_head.headers[header]

    def _delete(self, url):
        return self._session.delete(url=url,auth=self._basic_auth)
