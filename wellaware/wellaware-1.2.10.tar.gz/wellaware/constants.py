from __future__ import unicode_literals
from calendar import timegm
from copy import deepcopy
import logging

from wellaware import __version__
from wellaware._compat import *
from wellaware.auth.token import Token


logger = logging.getLogger('api-client')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


DEFAULT_TIMEOUT = 30
DEFAULT_BASE_URL = 'https://api.wellaware.us'
USER_AGENT = 'python_api_client/%s'.format(__version__)
DEFAULT_AUTH_HEADERS = {'Accept': 'application/json', 'user-agent': USER_AGENT}
DEFAULT_HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json', 'user-agent': USER_AGENT}


@add_metaclass(Singleton)
class Config(object):
    timeout = DEFAULT_TIMEOUT
    base_url = DEFAULT_BASE_URL
    user_agent = USER_AGENT
    auth_headers = DEFAULT_AUTH_HEADERS
    headers = DEFAULT_HEADERS
    include_token = False

Config()  # pre-call once


def make_headers(token):
    headers = deepcopy(Config.headers)
    if isinstance(token, string_types):
        headers['Authorization'] = token
    elif isinstance(token, Token):
        headers['Authorization'] = token.jwt
    return headers


def make_default_offset_limit(parameters={}):
    if parameters is None:
        parameters = {}
    if 'offset' not in parameters:
        parameters['offset'] = 0
    if 'limit' not in parameters:
        parameters['limit'] = 1000


def adjust_offset(parameters={}):
    make_default_offset_limit(parameters=parameters)
    parameters['offset'] += parameters['limit']


def datetime_to_ms(dt):
    if isinstance(dt, integer_types):
        return dt
    else:
        tmp = timegm(dt.utctimetuple())
        tmp += float(dt.microsecond) / 1000000.0
        return long_(tmp * 1000.0)


def chunk_list(iterable, size, pad_value=None):
    result = []
    for part in zip_longest(*[iter(iterable)]*size, fillvalue=pad_value):
        result.append([r for r in part if r is not None])
    return result


__all__ = ['Config', 'make_headers', 'logger', 'datetime_to_ms', 'make_default_offset_limit',
           'adjust_offset', 'chunk_list']
