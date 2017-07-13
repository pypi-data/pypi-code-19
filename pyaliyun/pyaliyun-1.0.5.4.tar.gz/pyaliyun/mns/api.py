#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
参考: https://help.aliyun.com/product/27412.html?spm=5176.doc35134.3.1.vkdmiJ
"""
import base64

from pyaliyun.core.api import BaseApi
from pyaliyun.core.encoding import force_bytes
from pyaliyun.core.request import AliRequest
from pyaliyun.core.utils import dict_to_xml


class MnsBaseApi(BaseApi):
    """
    消息服务 api
    """
    def __init__(self, host, account, schema="https", service="MNS"):
        """
        :param account:
        :param endpoint: http(s)://1698467070378510.mns.cn-hangzhou.aliyuncs.com/
        :param service:
        """
        self._version = "2015-06-06"
        self._content_type = "XML"
        self._xmlns = "http://mns.aliyuncs.com/doc/v1/"
        self._host = host
        self._schema = schema
        self._endpoint = "%s://%s" % (self._schema, self._host)
        self._header_prefix = "x-mns-"
        super(MnsBaseApi, self).__init__(account, service)

    def process_post_body(self, data, data_tag_name):
        if self._content_type == "XML":
            return dict_to_xml(data_tag_name, data, self._xmlns)
        else:
            return str(data)

    def get_request(self, resource, **kwargs):
        request = AliRequest(
            host=self._host,
            ak_id=self._account.access_key,
            ak_secret=self._account.access_secret,
            resource=resource,
            aliyun_service=self._service,
            header_prefix=self._header_prefix,
            method="POST",
            scheme="https"
        )
        request.add_headers({"x-mns-version": self._version})
        return request

class MnsQueueApi(MnsBaseApi):
    """
    消息服务 队列api
    """


    def send_message(self, queue_name, message_body, delay=0, priority=8):
        """
        https://help.aliyun.com/document_detail/35134.html?spm=5176.doc32295.6.686.ZZ6M35
        发送消息
        :return:
        """
        resource = '/queues/%s/messages' % queue_name
        origin_data = {
            "MessageBody": base64.b64encode(force_bytes(message_body)),
            "DelaySeconds": str(delay),
            "Priority": str(priority)
        }
        post_data = self.process_post_body(origin_data, "Message")
        ali_resp = self.post(post_data, resource)
        return ali_resp

    def __str__(self):
        return "MNS API SERVICE"

    def receive_message(self, queue_name, waitseconds=None):
        """
        消费消息
        https://help.aliyun.com/document_detail/35136.html?spm=5176.doc35131.6.688.rmU1qQ
        :param queue_name:
        :return:
        """
        resource = '/queues/%s/messages' % queue_name
        if waitseconds:
            resource = '/queues/%s/messages?waitseconds=%d' % (queue_name, int(waitseconds))
        ali_resp = self.get(resource)
        return ali_resp

    def delete_message(self, queue_name, receipt_handle):
        """
        删除消息
        :param test_queue:
        :param receipt_handle:
        :return:
        """
        resource = '/queues/%s/messages?ReceiptHandle=%s' % (queue_name, receipt_handle)
        ali_resp = self.delete(resource)
        return ali_resp


class MnsTopicApi(MnsBaseApi):
    """
    主题操作api
    """

    def send_message(self, topic_name, message_body, message_tag=None, message_attributes=None):
        """
        https://help.aliyun.com/document_detail/27497.html?spm=5176.doc27495.6.699.jm3t0R
        发送消息
        :return:
        """
        resource = '/topics/%s/messages' % topic_name
        origin_data = {
            "MessageBody": base64.b64encode(force_bytes(message_body)),
        }
        if message_tag:
            origin_data.update({"MessageTag": message_tag})
        if message_attributes:
            origin_data.update({"MessageAttributes": message_attributes})
        post_data = self.process_post_body(origin_data, "Message")
        ali_resp = self.post(post_data, resource)
        return ali_resp
