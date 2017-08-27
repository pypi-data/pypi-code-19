# coding=utf-8
# Copyright 2017 Flowdas Inc. <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from pkg_resources import get_distribution

__all__ = [
    '__author__',
    '__version__',
]

__author__ = u'오동권(Dong-gweon Oh) <prospero@flowdas.com>'
__version__ = getattr(get_distribution('launch'), 'version', None)
