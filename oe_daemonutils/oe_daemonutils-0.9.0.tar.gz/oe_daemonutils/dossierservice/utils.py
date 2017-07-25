# -*- coding: utf-8 -*-
import re
import sys
from collections import Mapping


def id_from_uri(uri):
    if uri is not None:
        res = re.search(r'[*/(\d+)]*$', uri).group(0)
        return int(res.lstrip('/')) if res else None
    else:
        return None


def is_empty_dossier(dossier_data):
    allowed_keys = ['id', 'self', 'uri']
    if len(dossier_data) == 1 and 'id' in dossier_data:
        return True
    if len(dossier_data) == 3 and all(key in allowed_keys for key in dossier_data.keys()):
        return True
    return False


def merge(src, changes):
    result = changes
    for key in src.keys():
        if key in changes:
            if isinstance(changes[key], Mapping):
                result[key] = merge(src[key], changes[key])
        else:
            result[key] = src[key]
    return result


# http://docs.pylonsproject.org/projects/pyramid/en/latest/_modules/pyramid/compat.html#text_
def text_(s, encoding='latin-1', errors='strict'):  # pragma: no cover
    """ If ``s`` is an instance of ``binary_type``, return
    ``s.decode(encoding, errors)``, otherwise return ``s``"""
    if sys.version_info[0] == 3:
        binary_type = bytes
    else:
        binary_type = str
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return s
