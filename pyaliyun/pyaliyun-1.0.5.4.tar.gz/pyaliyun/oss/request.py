#!/usr/bin/python
# -*- coding: utf-8 -*-
from ..core.request import AliRequest
from ..core.utils import buiild_canonicalized_headers, sign

__author__ = "vincent"
__email__ = "ohergal@gmail.com"
__copyright__ = "Copyright 2015, tiqiua.com"


class AliOssRequest(AliRequest):
    """
    基础请求包装类
    """

    def __init__(self,
                 host,
                 ak_id,
                 ak_secret,
                 resource,
                 aliyun_service,
                 bucket=None,
                 query_string=None,
                 content_type="text/xml;charset=UTF-8",
                 header_prefix=None,
                 headers=None,
                 method="GET",
                 scheme="http",
                 ):
        self.bucket = bucket
        self.query_string = query_string
        self.canonicalized_resource = '/' + bucket + resource
        super(AliOssRequest, self).__init__(host, ak_id, ak_secret, resource,
                                            aliyun_service, content_type,
                                            header_prefix, headers, method, scheme)

    def _sign(self, date, md5_hash):
        """
        签名
        :return:
        """

        canonicalized_headers = buiild_canonicalized_headers(self.headers, self.header_prefix)
        signature = sign(self.ak_secret,
                         self.method, md5_hash, self.content_type, date, self.canonicalized_resource, canonicalized_headers)
        return signature