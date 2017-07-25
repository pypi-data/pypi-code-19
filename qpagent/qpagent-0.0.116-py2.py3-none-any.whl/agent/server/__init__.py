#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import Bottle, run
import agent.config as config

app = Bottle()


def start_server():
    run(app, host='', port=config.port)
