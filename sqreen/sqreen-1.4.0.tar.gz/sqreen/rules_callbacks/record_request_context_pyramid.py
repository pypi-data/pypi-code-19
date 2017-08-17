# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Look for known crawlers user-agents
"""
from logging import getLogger

from ..rules import RuleCallback
from ..runtime_infos import runtime
from ..frameworks.pyramid_framework import PyramidRequest


LOGGER = getLogger(__name__)


class RecordRequestContextPyramid(RuleCallback):

    @staticmethod
    def pre(original, request):
        runtime.store_request(PyramidRequest(request))

    @staticmethod
    def post(*args, **kwargs):
        runtime.clear_request()

    @staticmethod
    def failing(*args, **kwargs):
        runtime.clear_request()
