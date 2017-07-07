from __future__ import unicode_literals

import logging
import os
import time
from hashlib import md5
from io import BytesIO

import requests
import xmltodict
from requests.compat import urljoin

from pymental.endpoints import JobEndpoint, JobProfileEndpoint
from pymental.errors import ClientError, ResourceValidationError

logger = logging.getLogger(__name__)


def parse_errors(content):
    """

    :param bytes content: a response's content
    :return:
    """
    root = xmltodict.parse(BytesIO(content))

    if 'errors' in root:
        errors = root['errors']
        if 'error' in errors:
            if isinstance(errors['error'], list):
                return [e for e in errors['error']]
            return errors['error']
    return []


class Conductor(object):
    def __init__(self, user=None, key=None, server_url=None):
        """
        :param str user:
        :param str key:
        :param str server_url:
        """
        self.user = user or os.environ.get('ELEMENTAL_USER')
        self.key = key or os.environ.get('ELEMENTAL_KEY')
        self.server_url = server_url or os.environ.get('ELEMENTAL_SERVER_URL')
        self.api_url = urljoin(self.server_url, '/api')

        self._session = requests.Session()
        self._session.headers['content-type'] = 'application/xml'
        self._session.headers['accept'] = 'application/xml'

        # endpoints
        self.jobs = JobEndpoint(self)
        self.profiles = JobProfileEndpoint(self)

    def _update_auth_headers(self, href, timeout=30):
        # TODO: some caching for the same url path authentication
        current_time = int(time.time())
        expires = str(current_time + timeout)

        auth_key = md5("{}{}".format(
                self.key,
                md5("{href}{user}{key}{expires}".format(
                        href=href,
                        user=self.user,
                        key=self.key,
                        expires=expires).encode()
                    ).hexdigest()
            ).encode()
        ).hexdigest()

        self._session.headers['X-Auth-User'] = self.user
        self._session.headers['X-Auth-Expires'] = expires
        self._session.headers['X-Auth-Key'] = auth_key

    def request(self, method, href, params=None, data=None):
        self._update_auth_headers(href)
        endpoint = urljoin(self.api_url, href)
        resp = self._session.request(method, endpoint, params=params, data=data)

        if resp.status_code == 422:
            errors = parse_errors(resp.content)
            raise ResourceValidationError(errors=errors)
        elif 400 <= resp.status_code < 600:
            raise ClientError(
                message='Reason: {}\nContent: {}'.format(
                    resp.reason,
                    parse_errors(resp.content)
                ),
                status_code=resp.status_code
            )

        return resp

    def get(self, href, params=None):
        return self.request('GET', href, params=params)

    def delete(self, href, params=None):
        return self.request('DELETE', href, params=params)

    def post(self, href, params=None, data=None):
        return self.request('POST', href, params=params, data=data)

    def close(self):
        self._session.close()
