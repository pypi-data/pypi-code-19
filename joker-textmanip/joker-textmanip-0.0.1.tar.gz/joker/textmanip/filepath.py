#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import os
import re
import sys


def keep_file_extension(old_path, new_path):
    _, old_ext = os.path.splitext(old_path)
    p, new_ext = os.path.splitext(new_path)
    if old_ext.lower() == new_ext.lower():
        return new_path
    return os.path.join(p, old_ext)


def url_to_filename(url):
    # http://stackoverflow.com/questions/295135/
    name = re.sub(r'[^\w\s-_.]+', '-', url)
    return re.sub(r'^{http|https|ftp}', '', name)


def under_home_dir(*paths):
    if sys.platform == 'win32':
        homedir = os.environ["HOMEPATH"]
    else:
        homedir = os.path.expanduser('~')
    return os.path.join(homedir, *paths)


def under_package_dir(package, *paths):
    p_dir = os.path.dirname(package.__file__)
    return os.path.join(p_dir, *paths)

