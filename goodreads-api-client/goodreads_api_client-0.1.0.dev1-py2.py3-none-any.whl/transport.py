# -*- coding: utf-8 -*-
"""
goodreads_api_client.transport
~~~~~

Contains transport underlying all requests made to the Goodreads API.
"""

from collections import OrderedDict
import json

import requests
import xmltodict


class Transport(object):
    """Makes requests to Goodreads API and applies transform to response."""

    def __init__(self, developer_key: str, base_url: str=None):
        """Initialize with credentials.

        :param str developer_key: Your Goodreads developer key. Find or
            generate one here <https://goodreads.com/api/keys>
        :param str/None base_url: Base URL of the Goodreads API.
            Defaults to https://goodreads.com.
        """
        if base_url is None:
            self.base_url = 'https://goodreads.com'
        else:
            self.base_url = base_url

        self.developer_key = developer_key

    def _req(self, method: str='GET', endpoint: str=None, params: dict=None,
             data: dict=None):
        if params is None:
            params = {}

        res = requests.request(
            method=method,
            url=f'{self.base_url}/{endpoint}',
            params={
                'key': self.developer_key,
                **params
            },
            data=data
        )

        res.raise_for_status()
        return res

    @staticmethod
    def _transform_res(res, transform: str='xml'):
        if transform == 'xml':
            content = xmltodict.parse(res.text)
            return content['GoodreadsResponse']
        if transform == 'json':
            content = json.loads(res.text)
            # This is just for consistency of return values across
            # different methods in this class - the ordering is not meaningful
            return OrderedDict(content.items())
        return res.text

    def req(self, method: str='GET', endpoint: str=None, params: dict=None,
            data: dict=None, transform: str='xml'):
        res = self._req(method, endpoint, params, data)
        return Transport._transform_res(res, transform)
