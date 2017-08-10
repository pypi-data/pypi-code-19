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

"""Config conversion."""
import builtins
import re
from configparser import ConfigParser

from mailman.utilities.modules import find_name


class ConfigConverter:
    """Converts a ConfigParser object values according to a schema."""

    def __init__(self, schema):
        self.schema = ConfigParser()
        self.schema.read_string(schema)

    def convert(self, cfg):
        """

        :param cfg:
        :type cfg: ConfigParser
        """
        out = dict()
        for section in self.schema.sections():
            out[section] = dict()
            for option in self.schema.options(section):
                out[section][option] = self._transform_option(section, option,
                                                              cfg.get(section,
                                                                      option))
        return out

    def converter(self, section, option):
        schema = self.schema.get(section, option)
        call = None
        try:
            call = getattr(builtins, schema)
        except:
            try:
                call = find_name(schema)
            except:
                if len(schema) != 0:
                    def call(value):
                        match = re.search(schema, value)
                        if match is None:
                            raise ValueError
                        return match.group()
        return call

    def _transform_option(self, section, option, value):
        call = self.converter(section, option)

        if call is None:
            raise ValueError
        else:
            return call(value)
