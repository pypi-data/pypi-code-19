import re

import requests

from .exceptions import ServerURLError

DOMAIN_REGEX = re.compile(r"http(s|)://(www\.|)(.+?)(/.*|)$")


def _api_path(server_url):
    _validate_server_url(server_url)
    if server_url[-1] != '/':
        server_url += '/'
    return server_url + 'api/'


def _validate_server_url(server_url):
    if not DOMAIN_REGEX.match(server_url):
        raise ServerURLError(server_url)


def _resource_url(server_url, resource_path):
    return _api_path(server_url) + resource_path


def make_get_json(name, resource_path):
    def func(server_url, *args, **kwargs):
        return requests.get(_resource_url(server_url, resource_path), *args, **kwargs).json()
    func.__name__ = name
    return func


def make_post_json(name, resource_path):
    def func(server_url, *args, **kwargs):
        return requests.post(_resource_url(server_url, resource_path), *args, **kwargs).json()
    func.__name__ = name
    return func
