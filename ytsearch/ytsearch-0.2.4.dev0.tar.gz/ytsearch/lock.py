#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import time


def create(lockfile):
    if not aquire(lockfile):
        return False

    with open(lockfile, 'w') as f:
        f.write('This file is protected!')
    return True


def aquire(lockfile, timeout=1, attempts=10):
    for i in range(10):
        if os.path.exists(lockfile):
            time.sleep(timeout)
        else:
            return True
    return False


def release(lockfile):
    os.remove(lockfile)
    return True
