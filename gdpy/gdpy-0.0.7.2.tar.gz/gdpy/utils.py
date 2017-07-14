# -*- coding:utf-8 -*-

import calendar
from email.utils import formatdate
import re
import sys
import inspect
import time
import json
from .compat import to_string, to_bytes
from ast import literal_eval

is_py2 = (sys.version_info[0] == 2)
is_py3 = (sys.version_info[0] == 3)


def get_current_function_name():
    return inspect.stack()[1][3]


def is_ip_or_localhost(netloc):
    """judge localhost or ip"""
    loc = netloc.split(':')[0]
    if loc == 'localhost':
        return True

    try:
        socket.inet_aton(loc)
    except socket.error:
        return False

    return True


if is_py2:
    def is_object_name_valid(name):
        if isinstance(name, (str, unicode)) is False:
            return False

        if re.match("^[a-zA-Z][\-a-zA-Z0-9_]{2,127}$", name) is None:
            return False

        return True
elif is_py3:
    def is_object_name_valid(name):
        if isinstance(name, (str)) is False:
            return False

        if re.match("^[a-zA-Z][\-a-zA-Z0-9_]{2,127}$", name) is None:
            return False

        return True


def is_object_version_valid(version):
    if isinstance(version, int) is False:
        return False

    if version <= 0:
        return False

    return True


def to_unixtime(time_string, format_string):
    return int(calendar.timegm(time.strptime(time_string, format_string)))


_GMT_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
_ISO8601_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"


def json_loader(unicode_body):
    if isinstance(unicode_body, bytes):
        unicode_body = unicode_body.decode('utf-8')
    return json.loads(unicode_body)


def json_dumper(data):
    return json.dumps(data)


def http_date(timeval=None):
    """
    return a string with HTTP standard GMT
    """
    return formatdate(timeval, usegmt=True)


def http_to_unixtime(time_string):
    """
    convert HTTP data string into Unix timestamp
    """
    return to_unixtime(time_string, _GMT_FORMAT)


def iso8601_to_unixtime(time_string):
    """
    convert ISO8601 string into Unix timestamp
    """
    return to_unixtime(time_string, _ISO8601_FORMAT)


def get_attribute(resp_text, attribute):
    return json.loads(resp_text).get(attribute, None)
