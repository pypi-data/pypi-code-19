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
import unittest

from pkg_resources import resource_filename, resource_string

from mailman_pgp.config import config
from mailman_pgp.config.config import Config
from mailman_pgp.config.validator import ConfigValidator
from mailman_pgp.testing.layers import PGPConfigLayer, PGPLayer


class TestConfig(unittest.TestCase):
    layer = PGPConfigLayer

    def test_name(self):
        self.assertEqual(config.name, 'pgp')


class TestConfigs(unittest.TestCase):
    layer = PGPLayer

    def setUp(self):
        self.validator = ConfigValidator(
                resource_string('mailman_pgp.config',
                                'schema.cfg').decode('utf-8'))

    def test_default_config(self):
        cfg = Config()
        cfg.read(resource_filename('mailman_pgp.config', 'mailman_pgp.cfg'))
        self.validator.validate(cfg)

    def test_testing_config(self):
        cfg = Config()
        cfg.read(resource_filename('mailman_pgp.testing', 'mailman_pgp.cfg'))
        self.validator.validate(cfg)
