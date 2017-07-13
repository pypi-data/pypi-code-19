#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

from pyaliyun.core.response import AliResponse

logger = logging.getLogger(__name__)


class BaseApi(object):
    def __init__(self, account, service=None, response_class=None):
        """
        service 为签名用到的如  OSS MNS 等等服务的名字
        :param account:
        :param service:
        """
        self._account = account
        self._service = service
        if not response_class:
            self.response_class = AliResponse
        else:
            self.response_class = response_class

    def get_request(self, resource, **kwargs):
        raise NotImplementedError

    def post(self, post_data, resource, **kwargs):
        req = self.get_request(resource)
        resp = req.post(post_data)
        ali_resp = self.response_class(self._service, resp)
        return ali_resp

    def put(self, put_data, resource, **kwargs):
        req = self.get_request(resource)
        resp = req.put(put_data)
        ali_resp = self.response_class(self._service, resp)
        return ali_resp

    def get(self, resource, **kwargs):
        req = self.get_request(resource)
        resp = req.get()
        ali_resp = self.response_class(self._service, resp)
        return ali_resp

    def delete(self, resource, **kwargs):
        req = self.get_request(resource)
        resp = req.delete()
        ali_resp = self.response_class(self._service, resp)
        return ali_resp
