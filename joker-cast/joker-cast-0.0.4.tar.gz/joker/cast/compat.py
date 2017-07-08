#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import os
import sys


def under_homedir(*paths):
    if sys.platform == 'win32':
        homedir = os.environ["HOMEPATH"]
    else:
        homedir = os.path.expanduser('~')
    return os.path.join(homedir, *paths)
