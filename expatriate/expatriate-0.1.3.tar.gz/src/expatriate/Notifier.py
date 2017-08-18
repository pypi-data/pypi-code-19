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

logger = logging.getLogger(__name__)

class Notifier(object):
    ''' class for a generic data structure that notifies a list of watchers when changes occur to the data contents '''

    def __init__(self):
        self._watchers = []

    def notify(self, watcher):
        ''' Add watcher of this data structure '''
        from .Watcher import Watcher
        if isinstance(watcher, Watcher):
            self._watchers.append(watcher)
        else:
            raise ListenerException(str(watcher) + ' does not inherit from Listener')

    def notify_added(self, additions):
        ''' Subclasses should call this method to notify watchers of additions. Argument is a (implementation dependent) list of additions. '''
        if not isinstance(additions, list):
            additions = [additions]
        for watcher in self._watchers:
            watcher.added(self, additions)

    def notify_updated(self, updates):
        ''' Subclasses should call this method to notify watchers of updates. Argument is a (implementation dependent) list of updates. '''
        if not isinstance(updates, list):
            updates = [updates]
        for watcher in self._watchers:
            watcher.updated(self, updates)

    def notify_deleted(self, deletion):
        ''' Subclasses should call this method to notify watchers of deletions. Argument is a (implementation dependent) list of deletions. '''
        if not isinstance(deletion, list):
            deletion = [deletion]
        for watcher in self._watchers:
            watcher.deleted(self, deletion)
