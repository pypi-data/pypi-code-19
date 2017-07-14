# Copyright (C) 2017 Jan Jancar
#
# This file is a part of the Mailman PGP plugin.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""Mailman PGP configuration module."""

from configparser import ConfigParser

from mailman.config import config as mailman_config
from mailman.utilities.modules import expand_path
from public.public import public


@public
class Config(ConfigParser):
    """A ConfigParser with a name."""

    def load(self, name):
        """
        Load the plugin configuration, and set our name.

        :param name: The name to set/load configuration for.
        :type name: str
        """
        self.name = name
        self.read(expand_path(
                dict(mailman_config.plugin_configs)[self.name].configuration))


config = Config()
public(config=config)
mm_config = mailman_config
public(mm_config=mm_config)
