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
import unittest

from mailman.testing.helpers import call_api

from mailman_pgp.config import config
from mailman_pgp.testing.layers import PGPRESTLayer


class TestConfig(unittest.TestCase):
    layer = PGPRESTLayer

    def setUp(self):
        pass

    def test_get_config(self):
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/config/')
        for section in config.sections():
            self.assertIn(section, json)
            json_section = json[section]
            for option in config.options(section):
                self.assertIn(option, json_section)
                self.assertEqual(config.get(section, option),
                                 json_section[option])

    def test_get_section(self):
        for section in config.sections():
            json, response = call_api(
                    'http://localhost:9001/3.1/plugins/pgp/config/' +
                    section + '/')
            for option in config.options(section):
                self.assertIn(option, json)
                self.assertEqual(config.get(section, option),
                                 json[option])

    def test_get_option(self):
        for section in config.sections():
            for option in config.options(section):
                json, response = call_api(
                        'http://localhost:9001/3.1/plugins/pgp/config/' +
                        section + '/' + option + '/')
                self.assertIn(option, json)
                self.assertEqual(config.get(section, option), json[option])
