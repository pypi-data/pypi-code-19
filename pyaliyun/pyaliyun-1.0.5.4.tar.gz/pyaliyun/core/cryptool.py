#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
加密解密的工具
"""

import base64
import hashlib

from pyaliyun.core.encoding import force_bytes, force_text

__author__ = "vincent"
__email__ = "ohergal@gmail.com"
__copyright__ = "Copyright 2015, tiqiua.com"


def b64encode_as_string(data):
    """
    base64编码后返回字符串
    :param data:
    :return:
    """
    return force_text(base64.b64encode(data))


def content_md5(data):
    """
    http的body计算content的md5的值, 返回字符串
    :param data:
    :return:
    """
    m = hashlib.md5(force_bytes(data))
    return b64encode_as_string(m.digest())


def md5_string(data):
    """
    返回md5编码的字符串
    :param data:
    :return:
    """
    return hashlib.md5(force_bytes(data)).hexdigest()
