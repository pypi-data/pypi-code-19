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

from unittest import TestCase

from mailman_pgp.config import config
from mailman_pgp.database import Database
from mailman_pgp.pgp import PGP
from mailman_pgp.testing.layers import PGPConfigLayer


class TestConfig(TestCase):
    layer = PGPConfigLayer

    def test_name(self):
        self.assertEqual(config.name, 'pgp')

    def test_sections(self):
        sections = sorted(['db', 'keydirs', 'keypairs', 'queues'])
        self.assertListEqual(sorted(config.sections()), sections)

    def test_db(self):
        self.assertTrue(hasattr(config, 'db'))
        self.assertIsInstance(config.db, Database)

    def test_pgp(self):
        self.assertTrue(hasattr(config, 'pgp'))
        self.assertIsInstance(config.pgp, PGP)
