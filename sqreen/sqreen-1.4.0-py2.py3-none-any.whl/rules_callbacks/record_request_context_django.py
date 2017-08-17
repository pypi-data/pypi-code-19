# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Look for known crawlers user-agents
"""
from logging import getLogger

from ..rules import RuleCallback
from ..runtime_infos import runtime
from ..frameworks.django_framework import DjangoRequest


LOGGER = getLogger(__name__)


class RecordRequestContextDjango(RuleCallback):

    @staticmethod
    def pre(original, request, view_func, view_args, view_kwargs):
        runtime.store_request(DjangoRequest(request, view_func, view_args, view_kwargs))

    @staticmethod
    def post(*args, **kwargs):
        runtime.clear_request()

    @staticmethod
    def failing(*args, **kwargs):
        """ Post is always called in a Django Middleware, don't clean the
        request right now as it may be needed in a post callback
        """
        pass
