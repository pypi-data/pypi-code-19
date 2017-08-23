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

from mailman_pgp.config import config
from mailman_pgp.database import transaction
from mailman_pgp.model.db_key import DBKey
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.testing.pgp import load_key


class TestDBKey(unittest.TestCase):
    layer = PGPConfigLayer

    def test_key(self):
        with transaction() as t:
            db_key = DBKey()
            t.add(db_key)

        key_data = load_key('rsa_1024.priv.asc')
        with transaction():
            db_key.key = key_data
        self.assertEqual(db_key.key.fingerprint, key_data.fingerprint)

    def test_loaded(self):
        key_data = load_key('rsa_1024.priv.asc')
        with transaction() as t:
            db_key = DBKey(key_data)
            t.add(db_key)

        config.db.scoped_session.remove()

        loaded_key = DBKey.query().one()
        self.assertEqual(loaded_key.key.fingerprint, key_data.fingerprint)
