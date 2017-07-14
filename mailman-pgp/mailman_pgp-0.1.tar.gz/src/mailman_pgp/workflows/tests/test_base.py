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
from contextlib import suppress
from unittest.mock import patch

from mailman.app.lifecycle import create_list
from mailman.interfaces.pending import IPendings
from mailman.interfaces.usermanager import IUserManager
from mailman.interfaces.workflows import IWorkflow
from mailman.testing.helpers import get_queue_messages
from mailman.workflows.common import SubscriptionBase
from public import public
from zope.component import getUtility
from zope.interface import implementer

from mailman_pgp.database import mm_transaction, transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.tests.base import load_key
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.workflows.base import (ConfirmPubkeyMixin, KEY_REQUEST,
                                        PGPMixin, SetPubkeyMixin)


class PubkeyMixinTestSetup():
    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')

        self.list_key = load_key('ecc_p256.priv.asc')

        self.pgp_list = PGPMailingList.for_list(self.mlist)
        self.pgp_list.key = self.list_key

        self.um = getUtility(IUserManager)

        self.sender_key = load_key('rsa_1024.priv.asc')
        self.sender = self.um.create_address('rsa-1024b@example.org')


@implementer(IWorkflow)
class PGPTestWorkflow(SubscriptionBase, PGPMixin, SetPubkeyMixin,
                      ConfirmPubkeyMixin):
    name = 'test-workflow'
    description = ''
    initial_state = 'prepare'
    save_attributes = (
        'pubkey_key',
        'pubkey_confirmed',
        'address_key',
        'subscriber_key',
        'user_key',
        'token_owner_key'
    )

    def __init__(self, mlist, subscriber=None, *, pubkey=None,
                 pubkey_pre_confirmed=False):
        SubscriptionBase.__init__(self, mlist, subscriber)
        SetPubkeyMixin.__init__(self, pubkey=pubkey)
        ConfirmPubkeyMixin.__init__(self, pre_confirmed=pubkey_pre_confirmed)
        PGPMixin.__init__(self)

    def _step_prepare(self):
        self.push('do_subscription')
        self.push('pubkey_confirmation')
        self.push('pubkey_checks')
        self.push('pgp_prepare')
        self.push('sanity_checks')


@public
class TestPGPMixin(PubkeyMixinTestSetup, unittest.TestCase):
    layer = PGPConfigLayer

    def test_create_address(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender)
        workflow.run_thru('pgp_prepare')
        pgp_address = PGPAddress.for_address(self.sender)
        self.assertIsNotNone(pgp_address)

    def test_address_existing(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender)
        with transaction() as t:
            pgp_address = PGPAddress(self.sender)
            t.add(pgp_address)
        workflow.run_thru('pgp_prepare')
        still = PGPAddress.for_address(self.sender)
        self.assertIsNotNone(still)


@public
class TestSetPubkeyMixin(PubkeyMixinTestSetup, unittest.TestCase):
    layer = PGPConfigLayer

    def test_key_request_sent(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender)
        list(workflow)
        items = get_queue_messages('virgin', expected_count=1)
        message = items[0].msg
        token = workflow.token

        self.assertEqual(message['Subject'], 'key set {}'.format(token))
        self.assertEqual(message.get_payload(), KEY_REQUEST)

    def test_receive_key(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender)
        list(workflow)
        with transaction():
            pgp_address = PGPAddress.for_address(self.sender)
            pgp_address.key = self.sender_key.pubkey

        receive_workflow = PGPTestWorkflow(self.mlist)
        receive_workflow.token = workflow.token
        receive_workflow.restore()
        receive_workflow.run_thru('receive_key')

    def test_set_pubkey(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender,
                                   pubkey=self.sender_key.pubkey)
        workflow.run_thru('pubkey_checks')
        pgp_address = PGPAddress.for_address(self.sender)
        self.assertIsNotNone(pgp_address)
        self.assertIsNotNone(pgp_address.key)
        self.assertEqual(pgp_address.key_fingerprint,
                         self.sender_key.fingerprint)

    def test_pubkey_set(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender)
        with transaction() as t:
            pgp_address = PGPAddress(self.sender)
            pgp_address.key = self.sender_key.pubkey
            t.add(pgp_address)
        workflow.run_thru('pubkey_checks')
        self.assertEqual(pgp_address.key_fingerprint,
                         self.sender_key.fingerprint)


@public
class TestConfirmPubkeyMixin(PubkeyMixinTestSetup, unittest.TestCase):
    layer = PGPConfigLayer

    def test_key_request_pubkey_set(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender,
                                   pubkey=self.sender_key.pubkey,
                                   pubkey_pre_confirmed=True)
        workflow.run_thru('pubkey_confirmation')
        with patch.object(workflow, '_step_do_subscription') as step:
            next(workflow)
        step.assert_called_once_with()

    def test_send_key_confirm_request(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender,
                                   pubkey=self.sender_key.pubkey,
                                   pubkey_pre_confirmed=False)
        list(workflow)
        items = get_queue_messages('virgin', expected_count=1)
        message = items[0].msg
        token = workflow.token

        self.assertEqual(message['Subject'], 'key confirm {}'.format(token))
        wrapped = PGPWrapper(message)
        self.assertTrue(wrapped.is_encrypted())

    def test_receive_confirmation(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender,
                                   pubkey=self.sender_key.pubkey,
                                   pubkey_pre_confirmed=False)
        list(workflow)

        receive_workflow = PGPTestWorkflow(self.mlist)
        receive_workflow.token = workflow.token
        receive_workflow.restore()
        receive_workflow.run_thru('receive_key_confirmation')
        with patch.object(receive_workflow, '_step_do_subscription') as step:
            next(receive_workflow)
        step.assert_called_once_with()


@public
class TestBothPubkeyMixins(PubkeyMixinTestSetup, unittest.TestCase):
    layer = PGPConfigLayer

    def test_pended_data_key_request(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender)
        with suppress(StopIteration):
            workflow.run_thru('send_key_request')
        self.assertIsNotNone(workflow.token)
        pendable = getUtility(IPendings).confirm(workflow.token, expunge=False)
        self.assertEqual(pendable['list_id'], 'test.example.com')
        self.assertEqual(pendable['email'], 'rsa-1024b@example.org')
        self.assertEqual(pendable['display_name'], '')
        self.assertEqual(pendable['when'], '2005-08-01T07:49:23')
        self.assertEqual(pendable['token_owner'], 'subscriber')

    def test_pended_data_key_confirmation(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender,
                                   pubkey=self.sender_key.pubkey)
        with suppress(StopIteration):
            workflow.run_thru('send_key_confirm_request')
        self.assertIsNotNone(workflow.token)
        pendable = getUtility(IPendings).confirm(workflow.token, expunge=False)
        self.assertEqual(pendable['list_id'], 'test.example.com')
        self.assertEqual(pendable['email'], 'rsa-1024b@example.org')
        self.assertEqual(pendable['display_name'], '')
        self.assertEqual(pendable['when'], '2005-08-01T07:49:23')
        self.assertEqual(pendable['token_owner'], 'subscriber')

    def test_exisitng_pgp_address(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender)

        with transaction() as t:
            pgp_address = PGPAddress(self.sender)
            pgp_address.key = self.sender_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        workflow.run_thru('pubkey_confirmation')
        with patch.object(workflow, '_step_do_subscription') as step:
            next(workflow)
        step.assert_called_once_with()

    def test_exisitng_pgp_address_not_confirmed(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender)

        with transaction() as t:
            pgp_address = PGPAddress(self.sender)
            pgp_address.key = self.sender_key.pubkey
            t.add(pgp_address)

        workflow.run_thru('pubkey_confirmation')
        with patch.object(workflow, '_step_send_key_confirm_request') as step:
            next(workflow)
        step.assert_called_once_with()

    def test_exisitng_pgp_address_no_key(self):
        workflow = PGPTestWorkflow(self.mlist, self.sender)

        with transaction() as t:
            pgp_address = PGPAddress(self.sender)
            t.add(pgp_address)

        workflow.run_thru('pubkey_checks')
        with patch.object(workflow, '_step_send_key_request') as step:
            next(workflow)
        step.assert_called_once_with()
