import sys
from urllib.parse import parse_qs

import requests
from requests_oauthlib import OAuth1

from .utils import _resource_url


def make_oauth_object(consumer_key, consumer_secret, resource_owner_key=None,
                      resource_owner_secret=None, secret_key=None):
    return OAuth1(client_key=consumer_key, client_secret=consumer_secret,
                  resource_owner_key=resource_owner_key,
                  resource_owner_secret=resource_owner_secret,
                  verifier=secret_key)


def _parse_response(response):
    creds = parse_qs(response.text)
    res = {}
    res['resource_owner_key'] = creds['oauth_token'][0]
    res['resource_owner_secret'] = creds['oauth_token_secret'][0]
    return res


def _default_oauth_callback(data):
    if not data.get('oauth_callback'):
        data.update({'oauth_callback': 'oob'})
    return data


def _make_post_oauth(name, resource_path):
    def func(server_url, *args, **kwargs):
        data = kwargs.get('data')
        if data:
            kwargs['data'] = _default_oauth_callback(data)
        resp = requests.post(_resource_url(server_url, resource_path), *args, **kwargs)
        return _parse_response(resp)
    func.__name__ = name
    return func


def make_path(path):
    return 'oauth/{}'.format(path)


for name in ('request_token', 'access_token'):
    setattr(sys.modules[__name__], name, _make_post_oauth(name, make_path(name)))


def authorize_url(server_url, resource_owner_key):
    return _resource_url(server_url, 'oauth/authorize') +\
        '?oauth_token=' + resource_owner_key
