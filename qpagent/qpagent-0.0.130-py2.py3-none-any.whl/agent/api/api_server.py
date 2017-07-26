#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import Bottle, run, request
from agent.config import config
from agent.util.adb import AdbTools
from agent.globalvar import get_queue
import json
import logging

logger = logging.getLogger(__name__)

app = Bottle()
a = AdbTools()


def start_api_server():
    run(app, host='', port=config["port"])


@app.post('/jobs')
def task():
    body = request.body
    get_queue().put(body)


@app.get('/ping')
def ping():
    return json.dumps(True)
