#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ram和sts的支持的产品列表
https://help.aliyun.com/knowledge_detail/39742.html?spm=5176.7839741.2.1.SFyJQf

"""

import logging

logger = logging.getLogger(__name__)


class Account(object):
    """
    账户类 里面保存ak等信息
    account_type M为主账户 S为子账户
    account_name 可以不填, 不填代表是主账户
    """

    def __init__(self,
                 access_key,
                 access_secret,
                 account_name=None,
                 account_type='M'):
        self.access_key = access_key
        self.access_secret = access_secret
        self.account_name = account_name
        self.account_type = account_type
