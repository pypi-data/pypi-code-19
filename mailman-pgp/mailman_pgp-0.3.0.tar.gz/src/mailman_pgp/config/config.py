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
import logging
from configparser import ConfigParser

from mailman.config import config as mailman_config
from mailman.utilities.modules import expand_path
from pkg_resources import resource_string
from public.public import public

from mailman_pgp.config.converter import ConfigConverter
from mailman_pgp.config.validator import ConfigValidator

log = logging.getLogger('mailman.plugin.pgp.config')


@public
class Config(ConfigParser):
    """A ConfigParser with a name."""

    def __init__(self):
        super().__init__()
        self.name = None
        self.dict = None
        schema = resource_string('mailman_pgp.config',
                                 'schema.cfg').decode('utf-8')
        self.validator = ConfigValidator(schema)
        self.converter = ConfigConverter(schema)

    def load(self, name):
        """
        Load the plugin configuration, and set our name.

        :param name: The name to set/load configuration for.
        :type name: str
        """
        self.name = name
        self.read(expand_path(
                dict(mailman_config.plugin_configs)[self.name].configuration))
        log.debug('Config loaded.')

    def validate(self):
        try:
            self.validator.validate(self)
        except ValueError:
            log.exception('Config did not validate.')
            raise
        log.debug('Config validated.')

    def convert(self):
        self.dict = self.converter.convert(self)
        log.debug('Config converted.')

    def get_value(self, section, option):
        return self.dict[section][option]

    def set(self, section, option, value=None):
        self.dict[section][option] = self.converter.converter(section, option)(
                value)
        return super().set(section, option, value)
