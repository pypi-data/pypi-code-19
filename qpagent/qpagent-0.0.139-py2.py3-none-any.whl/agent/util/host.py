#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket


def ip():
    global s
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        _ip = s.getsockname()[0]
    finally:
        s.close()

    return _ip


def name():
    return socket.gethostname()
