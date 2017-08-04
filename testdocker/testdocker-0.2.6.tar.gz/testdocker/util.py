"""
testdocker.util
~~~~~~~~~~~~~~~

Generic functions for testing docker containers.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import os
import re
import json
import mimetypes
import itertools
import subprocess


def shell(command, test_success=False):
    """Executes a shell command and returns the exit_code and output."""
    exit_code, output = subprocess.getstatusoutput(command)
    if test_success:
        return exit_code == 0
    return exit_code, output


def format_flag(name):
    """Formats a flag given the name."""
    return '--{}'.format(name.replace('_', '-'))


def set_defaults(obj1, obj2):
    """Recursively merge two objects, the second being the default object.

    Note: both objects need to be the same type.
    """
    assert type(obj1) is type(obj2)
    obj_class = type(obj1)
    if isinstance(obj1, (tuple, list)):
        obj1 = filter_dupes(obj1 + obj2)
    elif isinstance(obj1, dict):
        for key, val in obj2.items():
            if isinstance(val, (list, tuple)):
                obj1[key] = list(val) + obj1.get(key, [])
            elif isinstance(val, dict):
                obj1.setdefault(key, val)
            else:
                if key not in obj1:
                    obj1[key] = val
    return obj_class(obj1)


def filter_dupes(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def match(pattern, obj):
    """Returns true if pattern matches obj."""
    if isinstance(obj, str):
        return bool(re.search(pattern, obj))
    elif isinstance(obj, list):
        pattern = re.compile(pattern)
        for line in obj:
            if pattern.search(line):
                return True


def select_one(iterable, where, equals):
    """Returns the first object of iterable matching given attribute value."""
    for item in iterable:
        if getattr(item, where, None) == equals:
            return item


def filter_lines(lines, pattern):
    """Returns `lines` minus any line matching `pattern`."""
    if isinstance(lines, str):
        lines = lines.split('\n')
    regex = re.compile(pattern)
    lines = [line for line in lines if not regex.match(line)]
    return '\n'.join(lines)


def is_json(obj):
    """Returns `True` if `obj` passed is or contains json, `False` if not."""
    if os.path.isfile(obj):
        with open(obj) as fd:
            obj = fd.read()
    elif isinstance(obj, bytes):
        obj = obj.decode()
    try:
        json.loads(obj)
    except ValueError:
        return False
    return True


def get_content_type(path):
    """Returns an HTTP Content-type value for a few different mimetypes."""
    if is_json(path):
        content_type = 'application/json'
    else:
        content_type = mimetypes.guess_type(path)[0]

    if content_type and (
            content_type.startswith('text') or
            content_type.endswith('json')):
        content_type += '; charset=utf-8'
    return content_type
