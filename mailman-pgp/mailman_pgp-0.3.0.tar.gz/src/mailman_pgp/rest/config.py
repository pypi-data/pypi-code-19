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

""""""
from mailman.rest.helpers import etag, forbidden, not_found, okay

from mailman_pgp.config import config


class AConfig:
    """"""

    def __init__(self, section=None, option=None):
        self._section = section
        self._option = option

    def on_get(self, request, response):
        if not config.get_value('rest', 'allow_read_config'):
            forbidden(response)
            return
        if self._section is None:
            # return whole config
            resource = {}
            for section in config.sections():
                resource[section] = {key: config.get(section, key)
                                     for key in config.options(section)}
        else:
            if not config.has_section(self._section):
                not_found(response)
                return

            if self._option is None:
                # return section
                resource = {key: config.get(self._section, key)
                            for key in config.options(self._section)}
            else:
                if not config.has_option(self._section, self._option):
                    not_found(response)
                    return
                # return value
                resource = {self._option: config.get(self._section,
                                                     self._option)}
        okay(response, etag(resource))
