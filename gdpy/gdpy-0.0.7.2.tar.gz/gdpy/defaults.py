# -*- coding: utf-8 -*-

"""
gdpy.defaults
global variables
"""


def get(value, default_value):
    if value is None:
        return default_value
    else:
        return value


#: connect timeout
connect_timeout = 60

#: retry times
request_retries = 3

#: pool size for each session
connection_pool_size = 10
