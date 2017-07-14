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

from mailman.app.lifecycle import create_list
from mailman.interfaces.subscriptions import ISubscriptionManager, TokenOwner
from mailman.interfaces.usermanager import IUserManager
from mailman.testing.helpers import get_queue_messages
from public import public
from zope.component import getUtility

from mailman_pgp.database import mm_transaction, transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.tests.base import load_key
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.workflows.key_change import KeyChangeWorkflow


@public
class TestKeyChangeWorkflow(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')
        self.pgp_list = PGPMailingList.for_list(self.mlist)
        self.pgp_list.key = load_key('ecc_p256.priv.asc')

        self.sender_key = load_key('rsa_1024.priv.asc')
        self.sender_new_key = load_key('ecc_p256.priv.asc')
        self.sender = getUtility(IUserManager).create_address(
                'rsa-1024b@example.org')

    def test_pgp_address_none(self):
        workflow = KeyChangeWorkflow(self.mlist)
        with self.assertRaises(ValueError):
            list(workflow)

    def test_pubkey_none(self):
        with transaction() as t:
            pgp_address = PGPAddress(self.sender)
            t.add(pgp_address)

        workflow = KeyChangeWorkflow(self.mlist, pgp_address)
        with self.assertRaises(ValueError):
            list(workflow)

    def test_send_key_confirm_request(self):
        with transaction() as t:
            pgp_address = PGPAddress(self.sender)
            pgp_address.key = self.sender_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        workflow = KeyChangeWorkflow(self.mlist, pgp_address,
                                     self.sender_new_key.pubkey)
        list(workflow)
        items = get_queue_messages('virgin', expected_count=1)
        message = items[0].msg
        token = workflow.token

        self.assertEqual(message['Subject'], 'key confirm {}'.format(token))
        wrapped = PGPWrapper(message)
        self.assertTrue(wrapped.is_encrypted())

    def test_confirm(self):
        with transaction() as t:
            pgp_address = PGPAddress(self.sender)
            pgp_address.key = self.sender_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        workflow = KeyChangeWorkflow(self.mlist, pgp_address,
                                     self.sender_new_key.pubkey)
        list(workflow)

        token, token_owner, member = ISubscriptionManager(self.mlist).confirm(
                workflow.token)
        self.assertIsNone(token)
        self.assertEqual(token_owner, TokenOwner.no_one)

        pgp_address = PGPAddress.for_address(self.sender)
        self.assertEqual(pgp_address.key_fingerprint,
                         self.sender_new_key.fingerprint)
        self.assertTrue(pgp_address.key_confirmed)
