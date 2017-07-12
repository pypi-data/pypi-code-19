# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


from __future__ import (division, print_function, absolute_import,
                        unicode_literals)


import sys
import os

if sys.version_info.major == 2:
    str = unicode
    __chr__ = chr
    chr = unichr

if all(os.path.isdir(x) for x in ('bespon', 'test', 'doc')):
    sys.path.insert(0, '.')

import bespon.tooling as mdl
import bespon.erring as err

import pytest


def test_keydefaultdict():
    kd = mdl.keydefaultdict(lambda x: x**2)
    kd[2]
    kd[4]
    kd[8]
    assert(kd == {2:4, 4:16, 8:64})

    kd = mdl.keydefaultdict(lambda s: s)
    assert('key' not in kd)
    assert(kd['key'] == 'key')
    assert('key' in kd and len(kd) == 1)
