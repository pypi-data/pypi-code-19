# Copyright 2016 Casey Jaymes

# This file is part of Expatriate.
#
# Expatriate is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Expatriate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Expatriate.  If not, see <http://www.gnu.org/licenses/>.

import logging

from .exceptions import *
from .Notifier import Notifier

logger = logging.getLogger(__name__)

class NotifyingDict(dict, Notifier):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        Notifier.__init__(self)

    def __setitem__(self, key, value):
        if key not in self:
            r = dict.__setitem__(self, key, value)
            self.notify_added(key)
        else:
            r = dict.__setitem__(self, key, value)
            self.notify_updated(key)
        return r

    def __delitem__(self, key):
        r = dict.__delitem__(self, key)
        self.notify_deleted(key)
        return r

    def pop(self, *args):
        if args[0] in self:
            r = dict.pop(self, *args)
            self.notify_deleted(args[0])
            return r
        else:
            return dict.pop(self, *args)

    def popitem(self):
        r = dict.popitem(self)
        self.notify_deleted(r[0])
        return r

    def clear(self):
        k = list(self.keys())
        r = dict.clear(self)
        self.notify_deleted(k)
        return r

    def update(self, *args, **kwargs):
        if len(args) > 0 and isinstance(args[0], dict):
            keys = list(args[0].keys())
        elif len(args) > 0 and hasattr(args[0], '__iter__'):
            keys = []
            for k,v in args[0]:
                keys.append(k)
        else:
            keys = list(kwargs.keys())
        r = dict.update(self, *args, **kwargs)
        self.notify_updated(keys)
        return r

    def setdefault(self, *args):
        if args[0] in self:
            r = dict.setdefault(self, *args)
        else:
            r = dict.setdefault(self, *args)
            self.notify_added(args[0])
        return r
