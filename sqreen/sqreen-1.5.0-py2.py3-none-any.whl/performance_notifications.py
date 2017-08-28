# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Performance notifications related helpers
"""
import time

from logging import getLogger

LOGGER = getLogger(__name__)


class Timer(object):
    """ A context manager that time the duration of a block
    """

    __slots__ = ['key', 'start', 'stop']

    def __init__(self, key):
        self.key = key
        self.start = None
        self.stop = None

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop = time.time()

    def total_time(self):
        """ Compute the total running time of a block, return the running
        time in seconds as a float.
        """
        return self.stop - self.start
