# -*- coding: utf-8 -*-
"""Module containing client with resources of Goodreads API."""

from goodreads_api_client.exceptions import OauthEndpointNotImplemented
import goodreads_api_client.resources as resources
from goodreads_api_client.transport import Transport


class Client(object):
    """Makes API Calls to the Goodreads API <https://goodreads.com/api>."""

    def __init__(self, developer_key: str, base_url: str=None):
        """Initialize Goodreads API client with credentials.

        :param str developer_key: Your Goodreads developer key. Find or
            generate one here <https://goodreads.com/api/keys>
        :param str/None base_url: Base URL of the Goodreads API.
            Defaults to https://goodreads.com.
        """
        self._transport = Transport(developer_key, base_url)
        self._load_resources()

    def _load_resources(self):
        resource_dict = dict(
            [(name, cls) for name, cls in resources.__dict__.items()
             if isinstance(cls, type)])

        for resource_name, resource_cls in resource_dict.items():
            setattr(self, resource_name,
                    resource_cls(transport=self._transport))

    def auth_user(self):
        raise OauthEndpointNotImplemented('auth.user')

    def search_author(self, name: str):
        endpoint = f'api/author_url/{name}'
        res = self._transport.req(endpoint=endpoint)
        return res['author']

    def search_book(self, q: str, field: str='all', page: int=1):
        endpoint = 'search/index'
        params = {
            'field': field,
            'page': page,
            'q': q,
        }
        res = self._transport.req(endpoint=endpoint, params=params)
        return res['search']
