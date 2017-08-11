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

"""Config validation."""
from configparser import ConfigParser


class ConfigValidator:
    """Validates a ConfigParser object against a schema."""

    def __init__(self, schema):
        self.schema = ConfigParser()
        self.schema.read_string(schema)

    def validate(self, cfg):
        """

        :param cfg:
        :type cfg: ConfigParser
        """
        errors = []
        additional_sections = set(cfg.sections()).difference(
                self.schema.sections())

        if len(additional_sections) > 0:
            errors.append(
                    'Additional sections: {}'.format(additional_sections))

        for section in self.schema.sections():
            if not cfg.has_section(section):
                errors.append('Missing config section: {}'.format(section))
                continue
            for option in self.schema.options(section):
                if not cfg.has_option(section, option):
                    errors.append(
                            'Missing config option {} in {}'.format(option,
                                                                    section))
            additional_options = set(cfg.options(section)).difference(
                    self.schema.options(section))
            if len(additional_options) > 0:
                errors.append(
                        'Additional options: {}'.format(additional_options))

        if len(errors) > 0:
            raise ValueError(errors)
