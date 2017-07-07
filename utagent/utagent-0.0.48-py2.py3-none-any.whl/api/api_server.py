#!/usr/bin/env python
# -*- coding: utf-8 -*-

from slave.config import config
from bottle import Bottle, run, request
import slave.api.httpizza as api
import slave.util.sys_info as sysInfo
from slave.util.adb import AdbTools
from slave.globalvar import get_queue
import json
import logging

logger = logging.getLogger(__name__)

app = Bottle()
a = AdbTools()


def start_api_server():
    api.post_agent(sysInfo.get_host_ip(), config.API_PORT, sysInfo.get_host_name())
    api.post_device(sysInfo.get_host_ip(), a.get_device_brand(), a.get_device_model(), a.get_device_sdk_version(),
                    a.get_device_android_version(), a.get_device_id())
    run(app, host='', port=9099)


@app.post('/jobs')
def task():
    get_queue().put(request.body)


@app.get('/ping')
def ping():
    return json.dumps(True)
