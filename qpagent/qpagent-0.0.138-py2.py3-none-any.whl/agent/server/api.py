#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

from bottle import request

from agent.queue import q
from bottle import Bottle, run
import agent.config as config

app = Bottle()

logger = logging.getLogger(__name__)


def start_server():
    run(app, host='', port=config.port)


@app.post('/jobs')
def task():
    body = request.body
    q.put(body)


@app.get('/ping')
def ping():
    return json.dumps(True)
