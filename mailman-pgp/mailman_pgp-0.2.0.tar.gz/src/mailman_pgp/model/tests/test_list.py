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
from os.path import exists
from unittest import TestCase

from mailman.app.lifecycle import create_list
from mailman.interfaces.listmanager import IListManager
from zope.component import getUtility

from mailman_pgp.config import config
from mailman_pgp.database import mm_transaction
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.testing.pgp import load_key


class TestPGPMailingList(TestCase):
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

    def test_delete_key(self):
        self.addCleanup(config.set, 'keypairs', 'shred', 'yes')
        config.set('keypairs', 'shred', 'no')
        key_path = PGPMailingList.for_list(self.mlist).key_path
        getUtility(IListManager).delete(self.mlist)
        self.assertFalse(exists(key_path))
