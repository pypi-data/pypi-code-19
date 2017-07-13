#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
请求包装
"""

import requests

from pyaliyun.core.cryptool import content_md5
from pyaliyun.core.response import AliResponse
from .utils import buiild_canonicalized_headers, sign, get_date, build_header_authorization


class AliRequest(object):
    """
    基础请求包装类
    """

    def __init__(self,
                 host,
                 ak_id,
                 ak_secret,
                 resource,
                 aliyun_service,
                 content_type="text/xml;charset=UTF-8",
                 header_prefix=None,
                 headers=None,
                 method="GET",
                 scheme="http"):
        if headers is None:
            headers = {}
        self.host = host
        self.ak_id = ak_id
        self.ak_secret = ak_secret
        self.resource = resource
        self.aliyun_service = aliyun_service
        self.content_type = content_type
        self.headers = headers
        self.header_prefix = header_prefix
        self.request_body = None
        self.method = method
        self.scheme = scheme
        # 判断是否build完成, 初始化为False
        self.built = False
        self.request_url = "%s://%s%s" % (self.scheme, self.host, self.resource)

    def add_headers(self, data):
        """
        添加header值
        :param data:
        :return:
        """
        self.headers.update(data)

    def _sign(self, date, md5_hash):
        """
        签名
        :return:
        """

        canonicalized_headers = buiild_canonicalized_headers(self.headers, self.header_prefix)
        signature = sign(self.ak_secret,
                         self.method, md5_hash, self.content_type, date, self.resource, canonicalized_headers)
        return signature

    def _build(self):
        """
        构建请求
        :return:
        """
        date_string = get_date()
        if self.request_body:
            content_length = str(len(self.request_body))
        else:
            content_length = "0"
        md5_hash = ""
        if self.method == "POST" or self.method == "PUT":
            md5_hash = content_md5(self.request_body)
        self.headers.update(
            {
                "Content-Type": self.content_type,
                "Content-Length": content_length,
                "Content-Md5": md5_hash,
                "Date": date_string,
                "Host": self.host
            })
        signature = self._sign(date_string, md5_hash)
        authorization = build_header_authorization(self.aliyun_service, self.ak_id, signature)
        self.headers.update({"Authorization": authorization})
        self.built = True

    def _precondition(self):
        self._build()
        assert self.built, "Request has not been build"

    def post(self, data):
        """
        发送post请求
        :return:
        """
        self.method = "POST"
        self.request_body = data
        self._precondition()
        return requests.post(self.request_url, headers=self.headers, data=data)

    def put(self, data):
        """
        发送post请求
        :return:
        """
        self.method = "PUT"
        self.request_body = data
        self._precondition()
        return requests.put(self.request_url, headers=self.headers, data=data)

    def get(self):
        """
        发送get请求
        :return:
        """
        self.method = "GET"
        self._precondition()
        return requests.get(self.request_url, headers=self.headers)

    def delete(self):
        """
        delete请求
        :return:
        """
        self.method = "DELETE"
        self._precondition()
        return requests.delete(self.request_url, headers=self.headers)
