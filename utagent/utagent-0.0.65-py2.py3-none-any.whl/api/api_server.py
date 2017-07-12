#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import Bottle, run, request
from slave.config import config
from slave.util.adb import AdbTools
from slave.globalvar import get_queue
import json
import logging
import urllib

logger = logging.getLogger(__name__)

app = Bottle()
a = AdbTools()


def start_api_server():
    # api.post_device(sysInfo.get_host_ip(), a.get_device_brand(), a.get_device_model(), a.get_device_sdk_version(),
    #                 a.get_device_android_version(), a.get_device_id())
    run(app, host='', port=config["port"])


@app.post('/jobs')
def task():
    body = request.body
    get_queue().put(body)


@app.get('/ping')
def ping():
    return json.dumps(True)


if __name__ == '__main__':
    start_api_server()
