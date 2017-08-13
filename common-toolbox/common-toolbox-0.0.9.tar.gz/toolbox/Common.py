#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午3:26
# @Author  : Hou Rong
# @Site    : 
# @File    : Common.py
# @Software: PyCharm
from __future__ import unicode_literals

import six
from functools import partial, reduce
from operator import getitem


def is_legal(s):
    if s:
        if isinstance(s, six.string_types):
            if s.strip():
                if s.lower() != 'null':
                    return True
        elif isinstance(s, six.integer_types):
            if s > -1:
                return True

        elif isinstance(s, float):
            if s > -1.0:
                return True
    return False


def is_chinese(uchar):
    """
    :type uchar: unicode
    :return: bool
    """
    if "\u4e00" <= uchar <= "\u9fa5":
        return True
    else:
        return False


def key_modify(s):
    return s.strip().lower()


def get_or_default(a, b, default):
    """
    get b from a if exists else return default
    :param a:
    :param b:
    :param default:
    :return:
    """
    if isinstance(a, list):
        a = a[0]
    if hasattr(a, '__contains__'):
        if b in a:
            return getitem(a, b)
        else:
            return default
    else:
        return default


def dot_get(target_dict, *args, **kwargs):
    default = kwargs.get('default', '')
    if len(args) == 0:
        return default
    for arg in args:
        res = reduce(partial(get_or_default, default=default), arg.split('.'), target_dict)
        if res != default:
            return res
    return default


def i_do_not_care_list_or_dict(s):
    if isinstance(s, dict):
        yield s
    elif isinstance(s, list):
        for i in s:
            yield i
    elif isinstance(s, six.string_types):
        pass
    else:
        raise Exception("Unknown Type {0}".format(type(s)))
