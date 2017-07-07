# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
DataSync Watchers
"""

from __future__ import unicode_literals, absolute_import


class DataSyncWatcher(object):
    """
    Base class for all DataSync watchers.
    """
    prunes_changes = False
    retry_attempts = 1
    retry_delay = 1 # seconds

    def __init__(self, config, key):
        self.config = config
        self.key = key
        self.delay = 1 # seconds

    def setup(self):
        """
        This method is called when the watcher thread is first started.
        """

    def get_changes(self, lastrun):
        """
        This must be implemented by the subclass.  It should check the source
        database for pending changes, and return a list of
        :class:`rattail.db.model.DataSyncChange` instances representing the
        source changes.
        """
        return []

    def prune_changes(self, keys):
        """
        Prune change records from the source database, if relevant.
        """

    def process_changes(self, session, changes):
        """
        Process (consume) a batch of changes.
        """


class NullWatcher(DataSyncWatcher):
    """
    Null watcher, will never actually check for or report any changes.
    """


class ErrorTestWatcher(DataSyncWatcher):
    """
    Watcher which always raises an error when attempting to get changes.
    Useful for testing error handling etc.
    """

    def get_changes(self, lastrun):
        raise RuntimeError("Fake exception, to test error handling")
