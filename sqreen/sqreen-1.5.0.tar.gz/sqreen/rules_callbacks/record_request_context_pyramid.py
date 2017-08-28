# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Look for known crawlers user-agents
"""
from logging import getLogger

from ..runtime_infos import runtime
from ..frameworks.pyramid_framework import PyramidRequest
from .record_request_context import RecordRequestContext


LOGGER = getLogger(__name__)


class RecordRequestContextPyramid(RecordRequestContext):

    def pre(self, original, request):
        self._store_request(PyramidRequest(request))

    @staticmethod
    def post(*args, **kwargs):
        runtime.clear_request()

    @staticmethod
    def failing(*args, **kwargs):
        runtime.clear_request()
