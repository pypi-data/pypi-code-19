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
from mailman.interfaces.subscriptions import TokenOwner
from mailman.interfaces.usermanager import IUserManager
from mailman.interfaces.workflows import IWorkflow
from mailman.testing.helpers import get_queue_messages
from zope.component import getUtility
from zope.interface import implementer

from mailman_pgp.database import mm_transaction, transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.testing.pgp import load_key
from mailman_pgp.workflows.key_change import KeyChangeBase
from mailman_pgp.workflows.mod_approval import (
    ModeratorKeyChangeApprovalMixin)


@implementer(IWorkflow)
class PGPTestWorkflow(KeyChangeBase, ModeratorKeyChangeApprovalMixin):
    name = 'test-workflow'
    description = ''
    initial_state = 'mod_approval'
    save_attributes = (
        'approved',
    )

    def __init__(self, mlist, pgp_address=None, pubkey=None,
                 pre_approved=False):
        KeyChangeBase.__init__(self, mlist, pgp_address, pubkey)
        ModeratorKeyChangeApprovalMixin.__init__(self, pre_approved)


class TestModeratorApprovalMixin(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')
        with transaction():
            self.pgp_list = PGPMailingList.for_list(self.mlist)
            self.pgp_list.key = load_key('ecc_p256.priv.asc')

        self.sender_key = load_key('rsa_1024.priv.asc')
        self.sender_new_key = load_key('ecc_p256.priv.asc')
        self.sender = getUtility(IUserManager).create_address(
                'anne@example.org')

    def test_get_approval(self):
        with transaction() as t:
            pgp_address = PGPAddress(self.sender)
            pgp_address.key = self.sender_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        workflow = PGPTestWorkflow(self.mlist, pgp_address,
                                   self.sender_new_key.pubkey)
        list(workflow)
        items = get_queue_messages('virgin', expected_count=1)
        message = items[0].msg

        self.assertEqual(message['Subject'],
                         'New key change request from {}'.format(
                                 pgp_address.email))
        wrapped = PGPWrapper(message)
        self.assertTrue(wrapped.has_keys())
        keys = list(wrapped.keys())
        self.assertEqual(len(keys), 1)
        key = keys.pop()
        self.assertEqual(key.fingerprint, self.sender_new_key.fingerprint)

    def test_receive_approval(self):
        with transaction() as t:
            pgp_address = PGPAddress(self.sender)
            pgp_address.key = self.sender_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        workflow = PGPTestWorkflow(self.mlist, pgp_address,
                                   self.sender_new_key.pubkey)
        list(workflow)
        get_queue_messages('virgin', expected_count=1)
        list(workflow)
        self.assertEqual(workflow.token_owner, TokenOwner.no_one)
