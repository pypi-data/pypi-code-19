# -*- coding: utf-8; -*-
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
Upgrade handlers
"""

from __future__ import unicode_literals, absolute_import

import subprocess

from rattail.util import load_object


class UpgradeHandler(object):
    """
    Base class and default implementation for upgrade handlers.
    """

    def __init__(self, config):
        self.config = config

    def executable(self, upgrade):
        """
        This method should return a boolean indicating whether or not execution
        should be allowed for the upgrade, given its current condition.  The
        default simply returns ``True`` but you may override as needed.

        Note that this (currently) only affects the enabled/disabled state of
        the Execute button within the Tailbone upgrade view.
        """
        if upgrade is None:
            return True
        return not bool(upgrade.executed)

    def execute(self, upgrade, user, progress=None, **kwargs):
        """
        Execute the given upgrade, as the given user.
        """
        cmd = self.config.upgrade_command()
        stdout_path = self.config.upgrade_filepath(upgrade.uuid, filename='stdout.log', makedirs=True)
        stderr_path = self.config.upgrade_filepath(upgrade.uuid, filename='stderr.log')
        with open(stdout_path, 'wb') as stdout:
            with open(stderr_path, 'wb') as stderr:
                subprocess.call(cmd, stdout=stdout, stderr=stderr)


def get_upgrade_handler(config, default=None):
    """
    Returns an upgrade handler object.
    """
    spec = config.get('rattail.upgrades', 'handler', default=default)
    if spec:
        handler = load_object(spec)(config)
    else:
        handler = UpgradeHandler(config)
    return handler
