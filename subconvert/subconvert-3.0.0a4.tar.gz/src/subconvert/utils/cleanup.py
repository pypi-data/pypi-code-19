# Copyright (C) 2017 Michał Góral.
#
# This file is part of Subconvert
# 
# Subconvert is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Subconvert is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Subconvert. If not, see <http://www.gnu.org/licenses/>.
#
#
# This file contains code which was borrowed from FeedCommas:
# https://gitlab.com/mgoral/feed-commas

'''Global during shutdown handler. Any client code might register cleanup
functions, which will be called upon a shutdown in order they were
registered.'''

import sys
import functools


class Cleanup:
    '''Cleanupper'''
    def __init__(self):
        self._clean = []

    def register(self, func, *args, **kwargs):
        '''Adds a cleanup function. It will be called with a given args and
        kwargs when the time will come.'''
        self._clean.append(functools.partial(func, *args, **kwargs))

    def start(self):
        '''Calls all handlers in reverse order as they were registered. All
        handlers are called, even if one of them raises an exception. Last
        exception is re-raised after that.'''
        einfo = None
        while self._clean:
            handler = self._clean.pop()
            try:
                handler()
            except:
                einfo = sys.exc_info()

        if einfo is not None:
            raise einfo[1]


cleanup = Cleanup()
