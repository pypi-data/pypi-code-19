# -*- coding:utf-8 -*-

"""
gdpy.exceptions
"""

import re

from .compat import to_string, to_bytes
from .utils import json_loader


_GD_ERROR_TO_EXCEPTION = {}


GD_CLIENT_ERROR_STATUS = -1
GD_REQUEST_ERROR_STATUS = -2
GD_INCONSISTENT_ERROR_STATUS = -3


class GDError(Exception):
    def __init__(self, status, headers, error_message, error_code, error_message_chs):
        #: HTTP status code
        self.status = status

        #: id to track a request
        self.request_id = headers.get('x-gd-request-id', '')

        #: HTTP body
        self.error_message = error_message

        #: error code
        self.code = error_code

        #: error message chs
        self.error_message_chs = error_message_chs

    def __str__(self):
        error = {'status': self.status,
                 'details': self.error_message}
        return str(error)


class RequestError(GDError):
    def __init__(self, e):
        GDError.__init__(self, GD_REQUEST_ERROR_STATUS, {}, 'RequestError: ' + str(e), {}, {})
        self.exception = e

    def __str__(self):
        error = {'status': self.status,
                 'details': self.error_message}
        return str(error)


class ServerError(GDError):
    pass


class ClientError(GDError):
    pass


def make_exception(resp):
    status = resp.status
    headers = resp.headers
    body = _parse_error_resp(resp)
    error_message = to_bytes(body.get('error_message'))
    error_code = to_bytes(body.get('error_code'))
    error_message_chs = to_bytes(body.get('error_message_chs'))
    return ServerError(status, headers, error_message, error_code, error_message_chs)


def _parse_error_resp(resp):
    try:
        return json_loader(resp.response.text)
    except ValueError as e:
        if resp.status >= 500:
            raise ServerError(resp.status, {}, resp.response.text, str(resp.status), resp.response.text)
        else:
            raise e
