#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket


def get_host_ip():
    global s
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def get_host_name():
    return socket.gethostname()
