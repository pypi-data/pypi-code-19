#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
阿里云的响应包装
    提供以下方便的属性
    service 服务, 如 MNS
    interface 业务, 如CreateQueue
    host_id 主机名
    request_id  请求id
    error_code 直接拿出错误代码比如 UnsupportedOperation
    error_msg  错误消息 如 The specified action is not supported.
    is_success 是否成功 True or False
    content_data 转换后的数据 xml转成dict, json的数据就是json
    prefix header里的前缀 如 x-oss-

    其他属性
    status_code
    encoding
    content_type
"""
from pyaliyun.core.constant import ALI_CONTENT_TYPE_XML, ALI_CONTENT_TYPE_JSON
from pyaliyun.core.exception import PyAliErrorResponseException
from pyaliyun.core.xmltools import XmlDecoder


class AliResponse(object):
    def __init__(self, service, resp):
        self.service = service
        self._resp = resp
        self.headers = resp.headers
        self.header_prefix = "x-%s-" % str(service).lower()

        self.error_code = None
        self.error_msg = None
        self.host_id = None
        self.request_id = None

        self._process()

    def _process(self):
        """
        处理数据
        :return:
        """
        # 数据类型
        self._process_result()
        self._process_content()
        self._process_general_info()

    def _process_general_info(self):
        """
        处理其他通用信息
        :return:
        """
        if not self.is_success:
            # 不成功,提取错误消息等等数据
            if self.content_type in ALI_CONTENT_TYPE_XML:
                self.error_code = XmlDecoder.get_document(self.content_data['Error']['Code'])
                self.error_msg = XmlDecoder.get_document(self.content_data['Error']['Message'])
                self.host_id = XmlDecoder.get_document(self.content_data['Error']['HostId'])
                self.request_id = XmlDecoder.get_document(self.content_data['Error']['RequestId'])
            if self.content_type in ALI_CONTENT_TYPE_JSON:
                self.error_code = self.content_data['Code']
                self.error_msg = self.content_data['Message']
                self.host_id = self.content_data['HostId']
                self.request_id = self.content_data['RequestId']
        else:
            # 成功之后
            request_id_header_key = "%srequest-id" % self.header_prefix
            # 先从header里检查
            if request_id_header_key in self.headers:
                self.request_id = self.headers[request_id_header_key]
            if self.content_type in ALI_CONTENT_TYPE_XML:
                # self.host_id = XmlDecoder.get_document(self.content_data['Error']['HostId'])
                # self.request_id = XmlDecoder.get_document(self.content_data['Error']['RequestId'])
                pass
            if self.content_type in ALI_CONTENT_TYPE_JSON:
                # json的有的在content里
                if 'RequestId' in self.content_data:
                    self.request_id = self.content_data['RequestId']

    def _process_result(self):
        """
        判断结果
        :return:
        """
        self.status_code = self._resp.status_code
        if self.status_code >= 300:
            self.is_success = False
        elif 300 > self.status_code >= 200:
            self.is_success = True
        else:
            raise PyAliErrorResponseException("ErrorStatus", "Unknown Status Code", code=self.status_code)

    def _process_content(self):
        """
        内容数据处理
        :return:
        """
        self.encoding = self._resp.encoding
        self.content_type = self.headers.get('content-type')
        if self.content_type in ALI_CONTENT_TYPE_XML:
            self.content_data = XmlDecoder.xml_to_dict(self._resp.text)
        elif self.content_type in ALI_CONTENT_TYPE_JSON:
            self.content_data = self._resp.json
