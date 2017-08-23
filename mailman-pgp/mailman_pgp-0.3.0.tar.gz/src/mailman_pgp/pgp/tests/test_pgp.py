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

"""Tests for the module global PGP instance."""
import unittest

from mailman.app.lifecycle import create_list
from mailman.testing.helpers import subscribe

from mailman_pgp.config import config
from mailman_pgp.database import mm_transaction, transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.keygen import ListKeyGenerator
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.testing.pgp import load_key


class TestPGP(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')
        self.pgp_list = PGPMailingList.for_list(self.mlist)
        self.list_key = ListKeyGenerator(self.pgp_list).generate(True)

        # Make Anne a member of this mailing list.
        self.anne = subscribe(self.mlist, 'Anne', email='anne@example.org')
        self.anne_key = load_key('rsa_1024.priv.asc')

        with transaction() as t:
            self.pgp_anne = PGPAddress(self.anne.address)
            self.pgp_anne.key = self.anne_key.pubkey
            self.pgp_anne.key_confirmed = True
            t.add(self.pgp_anne)

    def test_list_keydir(self):
        keyring = config.pgp.list_keyring
        self.assertEqual(len(keyring), 2)
        with keyring.key(self.pgp_list.mlist.fqdn_listname) as key:
            self.assertEqual(key.fingerprint, self.list_key.fingerprint)

    def test_user_keydir(self):
        keyring = config.pgp.user_keyring
        self.assertEqual(len(keyring), 2)
        with keyring.key(self.anne_key.fingerprint) as key:
            self.assertTrue(key.is_public)
            self.assertEqual(key.fingerprint, self.anne_key.fingerprint)

    def test_archive_keydir(self):
        keyring = config.pgp.archive_keyring
        self.assertEqual(len(keyring), 0)
