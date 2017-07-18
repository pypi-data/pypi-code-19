#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import struct
import subprocess
try:
    from .. import frozen
except ImportError:
    frozen = False


DEFAULT_PORT = 8587
DEFAULT_HOST = 'localhost'
WATCHDOG_STARTSTOP_TIMEOUT = 0
WATCHDOG_CALL_TIMEOUT = 0.3
MULTICOLUMN_NAME = 'allfiles.out'
PICKLE_MAGIC_NUMBER = 0xdeadbeef
PICKLE_HEADER_STRUCT = 'QQ'
PICKLE_HEADER_SIZE = struct.calcsize(PICKLE_HEADER_STRUCT)


def get_hg_hash():
    if not get_hg_hash.hash:
        # noinspection PyUnresolvedReferences
        if hasattr(sys, 'frozen') or frozen:
            get_hg_hash.hash = frozen.hg_hash
        else:
            path = os.path.dirname(os.path.dirname(__file__))
            try:
                pipe = subprocess.Popen(['hg', 'id', '-i', '-R', path], stdout=subprocess.PIPE)
                get_hg_hash.hash = pipe.stdout.read().decode()
            except OSError:
                get_hg_hash.hash = 'unknown'
        get_hg_hash.hash = get_hg_hash.hash.strip()
    return get_hg_hash.hash
get_hg_hash.hash = ''
