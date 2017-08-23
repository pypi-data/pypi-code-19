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
import shutil
import unittest
from os.path import exists

from mailman.app.lifecycle import create_list
from mailman.interfaces.listmanager import IListManager
from zope.component import getUtility

from mailman_pgp.database import mm_transaction
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.testing.config import patch_config
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.testing.pgp import load_key


class TestPGPMailingList(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')
        pgp_list = PGPMailingList.for_list(self.mlist)
        pgp_list.key = load_key('rsa_1024.priv.asc')

    def test_delete(self):
        getUtility(IListManager).delete(self.mlist)
        pgp_list = PGPMailingList.for_list(self.mlist)
        self.assertIsNone(pgp_list)

    def test_shred_key(self):
        key_path = PGPMailingList.for_list(self.mlist).key_path
        getUtility(IListManager).delete(self.mlist)
        self.assertFalse(exists(key_path))

    @patch_config('keypairs', 'shred_command', 'shred')
    @unittest.skipIf(shutil.which('shred') is None, 'No shred command.')
    def test_shred_key_command(self):
        # This really just hopes that the test env has some coreutils, that
        # provide `shred` command with this behaviour.
        key_path = PGPMailingList.for_list(self.mlist).key_path
        with open(key_path, 'rb') as f:
            before = f.read()
        getUtility(IListManager).delete(self.mlist)
        with open(key_path, 'rb') as f:
            after = f.read()
        self.assertNotEqual(before, after)

    @patch_config('keypairs', 'shred', 'no')
    def test_delete_key(self):
        key_path = PGPMailingList.for_list(self.mlist).key_path
        getUtility(IListManager).delete(self.mlist)
        self.assertFalse(exists(key_path))
