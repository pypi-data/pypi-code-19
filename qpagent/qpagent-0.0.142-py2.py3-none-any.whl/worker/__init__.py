#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


def make_worker_dir(path):
    try:
        if os.path.isdir(path):
            pass
        else:
            os.makedirs(path)
        return path
    except Exception, e:
        print(e)
