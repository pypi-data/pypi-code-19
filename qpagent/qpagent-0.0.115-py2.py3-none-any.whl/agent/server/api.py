#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

from bottle import request

from agent.queue import q
from . import app

logger = logging.getLogger(__name__)


@app.post('/jobs')
def task():
    body = request.body
    q.put(body)


@app.get('/ping')
def ping():
    return json.dumps(True)
