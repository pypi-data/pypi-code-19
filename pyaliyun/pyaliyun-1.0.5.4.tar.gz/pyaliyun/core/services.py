#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
包装服务信息
"""


class AliService(object):
    def __init__(self, name):
        self.name = name

    def get_header_prefix(self):
        raise NotImplementedError

    def get_business(self):
        raise NotImplementedError
