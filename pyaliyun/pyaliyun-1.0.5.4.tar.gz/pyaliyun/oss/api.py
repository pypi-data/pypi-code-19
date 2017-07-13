#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
参考: https://help.aliyun.com/product/31815.html?spm=5176.doc31935.3.1.wb3Fy5
"""
import base64
import time
from datetime import timedelta, datetime
from time import gmtime

from pyaliyun.core.api import BaseApi
from pyaliyun.core.encoding import force_str
from pyaliyun.core.request import AliRequest
from pyaliyun.oss.request import AliOssRequest


class Helper(BaseApi):
    """
    some useful api tools
    """

    def __init__(self, host, account, schema="http", service="OSS"):
        self._host = host
        self._schema = schema
        self._endpoint = "%s://%s" % (self._schema, self._host)
        self._header_prefix = "x-oss-"
        super(Helper, self).__init__(account, service)

    def get_policy(self, size=10):
        """
            表单提交到oss的方法需要能获取一个policy的编码数据
            这里将过期时间延后一个小时
            """
        # 获取gmt时间
        gmt_struct = gmtime()
        # struct 转化成time对象
        gmt_time = time.mktime(gmt_struct)
        # 转datetime
        gmt_dt = datetime.fromtimestamp(gmt_time)
        # 获取 开始后的10分钟, 10分钟后过期
        timeout_delta = timedelta(minutes=10)
        policy_gmt_dt = gmt_dt + timeout_delta
        # 组成json字符串
        policy_gmttime = policy_gmt_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        file_size = 1024 * 1024 * size
        policy_json = '{"expiration": "%s","conditions": [["content-length-range"' \
                      ', 0, %d]]}' % (policy_gmttime, file_size)
        # % gmt_time
        # 转化utf8
        policy_json_utf8 = force_str(policy_json)
        # 进行base64编码
        policy_value = base64.standard_b64encode(policy_json_utf8).strip()
        return policy_value


class OssBaseApi(BaseApi):
    """
    OSS base api
    https://help.aliyun.com/document_detail/31947.html?spm=5176.doc31978.6.834.am7U9m
    """

    def __init__(self, host, account, schema="http", service="OSS"):
        """
        :param account:
        :param endpoint: http(s)://1698467070378510.mns.cn-hangzhou.aliyuncs.com/
        :param service:
        """
        self._host = host
        self._schema = schema
        self._endpoint = "%s://%s" % (self._schema, self._host)
        self._header_prefix = "x-oss-"
        super(OssBaseApi, self).__init__(account, service)

    def get_request(self, resource, **kwargs):
        request = AliRequest(
            host=self._host,
            ak_id=self._account.access_key,
            ak_secret=self._account.access_secret,
            resource=resource,
            aliyun_service=self._service,
            content_type='image/jpeg',
            header_prefix=self._header_prefix,
            method="POST",
            scheme="https"
        )
        return request


class OssObjectApi(OssBaseApi):
    def __init__(self, bucket, host, account, schema="http", service="OSS"):
        self._bucket = bucket
        super(OssObjectApi, self).__init__(host, account, schema, service)

    def get_request(self, resource, **kwargs):
        request = AliOssRequest(
            host=self._host,
            ak_id=self._account.access_key,
            ak_secret=self._account.access_secret,
            resource=resource,
            aliyun_service=self._service,
            bucket=self._bucket,
            header_prefix=self._header_prefix,
            method="POST",
            scheme="https"
        )
        return request

    def put(self, put_data, resource, **kwargs):
        req = self.get_request(resource)
        if 'content_type' in kwargs.keys():
            req.content_type = kwargs['content_type']
        resp = req.put(put_data)
        ali_resp = self.response_class(self._service, resp)
        return ali_resp

    def put_object(self, key, data, content_type):
        """
        上传文件, 返回访问地址
        :return:
        """

        resource = key
        ali_resp = self.put(data, resource, content_type=content_type)
        return ali_resp
