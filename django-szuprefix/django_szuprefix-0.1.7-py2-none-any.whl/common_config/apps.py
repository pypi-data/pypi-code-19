#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:denishuang

from __future__ import unicode_literals

from django.apps import AppConfig


class CommonConfigConfig(AppConfig):
    name = 'django_szuprefix.common_config'
    #label = 'common_config'
    verbose_name = (u'通用配置')

    def ready(self):
        super(CommonConfigConfig, self).ready()
        from . import receivers