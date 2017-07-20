#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiprocessing import Queue

q = Queue()


def get_queue():
    return q
