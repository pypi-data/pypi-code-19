#!/usr/bin/env python
# -*- coding: utf-8 -*-

def monitor_worker_ok(**kw):
    """监控系统监测worker status
    """
    if not kw.get('web_ip', ''):
        raise ValueError(950, u'请求ip不能为空')
