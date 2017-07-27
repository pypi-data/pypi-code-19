# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import threading

from django.utils.deprecation import MiddlewareMixin


class GlobalRequestMiddleware(MiddlewareMixin):
    thread_local = threading.local()

    def process_request(self, request):
        GlobalRequestMiddleware.thread_local.request = request

    def process_response(self, request, response):
        GlobalRequestMiddleware.thread_local.request = None
        return response
