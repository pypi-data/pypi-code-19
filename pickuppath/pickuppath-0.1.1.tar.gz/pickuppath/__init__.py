# -*- coding:utf-8 -*-
import logging
import os.path
logger = logging.getLogger(__name__)


def pickup_path(filename, current=None, default=None):
    """pickupping the config file path

    start path = "/foo/bar/boo", filename = "config.ini"
    finding candidates are ["/foo/bar/boo/config.ini", "/foo/bar/config.ini", "/foo/config.ini", "/config.ini"]
    """
    current = current or os.getcwd()
    start_point = os.path.normpath(os.path.abspath(current))
    current = start_point
    candidates = []
    while True:
        candidates.append(os.path.join(current, filename))
        if current == "/":
            break
        current, dropped = os.path.split(current)

    for path in candidates:
        logger.debug("check: %s", path)
        if os.path.exists(path):
            return path
    return default
