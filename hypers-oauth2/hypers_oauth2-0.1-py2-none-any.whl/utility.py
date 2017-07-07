# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import requests


def post(url, data, headers):
    r = requests.post(url, data=data, headers=headers)
    result = r.json()

    # 获取token失败
    if 'error' in result:
        raise APIError(result['error'], result.get('error_description'))

    return result


class APIError(Exception):
    """raise APIError if receiving json message indicating failure."""
    def __init__(self, error, error_description):
        self.error = error
        self.error_description = error_description
        Exception.__init__(self, error)

    def __str__(self):
        return 'APIError: %s: "%s"' % (self.error, self.error_description)
