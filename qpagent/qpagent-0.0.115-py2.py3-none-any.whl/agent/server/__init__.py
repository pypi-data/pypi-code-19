#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import Bottle, run
from ..config import port

app = Bottle()


def start_server():
    run(app, host='', port=port)
