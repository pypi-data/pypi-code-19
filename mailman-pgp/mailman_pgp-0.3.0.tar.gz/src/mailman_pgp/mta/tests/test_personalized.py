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

"""Test the PGP enabled IndividualDelivery."""
import unittest

from mailman.app.lifecycle import create_list
from mailman.interfaces.mailinglist import Personalization
from mailman.testing.helpers import (
    specialized_message_from_string as mfs, subscribe)

from mailman_pgp.database import transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.mta.personalized import PGPPersonalizedDelivery
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.testing.pgp import load_key
from mailman_pgp.utils.pgp import verifies


class PersonalizedDeliveryTester(PGPPersonalizedDelivery):
    """Save the deliveries made by the PGPPersonalizedDelivery class."""

    def __init__(self):
        super().__init__()
        self.deliveries = []

    def _deliver_to_recipients(self, mlist, msg, msgdata, recipients):
        self.deliveries.append((mlist, msg, msgdata, recipients))
        return []


class TestPGPPersonalizedDelivery(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        self.mlist = create_list('test@example.com', style_name='pgp-default')
        self.mlist.personalize = Personalization.individual

        self.list_key = load_key('ecc_p256.priv.asc')
        self.pgp_list = PGPMailingList.for_list(self.mlist)
        self.pgp_list.key = self.list_key

        # Make Anne a member of this mailing list.
        self.anne = subscribe(self.mlist, 'Anne', email='anne@example.org')
        self.anne_key = load_key('rsa_1024.priv.asc')
        with transaction() as t:
            self.pgp_anne = PGPAddress(self.anne.address)
            self.pgp_anne.key = self.anne_key.pubkey
            self.pgp_anne.key_confirmed = True
            t.add(self.pgp_anne)

        # Clear out any results from the previous test.
        self.msg = mfs("""\
From: anne@example.org
To: test@example.com
Subject: test

""")

    def test_sign_encrypt(self):
        with transaction():
            self.pgp_list.sign_outgoing = True
            self.pgp_list.encrypt_outgoing = True

        msgdata = dict(recipients=['anne@example.org'])
        agent = PersonalizedDeliveryTester()
        refused = agent.deliver(self.mlist, self.msg, msgdata)

        self.assertEqual(len(refused), 0)
        self.assertEqual(len(agent.deliveries), 1)

        out_msg = agent.deliveries[0][1]
        out_wrapped = PGPWrapper(out_msg)
        self.assertTrue(out_wrapped.is_encrypted())

        decrypted = out_wrapped.copy().decrypt(self.list_key)
        self.assertTrue(decrypted.is_signed())

        decrypted = out_wrapped.copy().decrypt(self.anne_key)
        self.assertTrue(decrypted.is_signed())

    def test_encrypt(self):
        with transaction():
            self.pgp_list.sign_outgoing = False
            self.pgp_list.encrypt_outgoing = True

        msgdata = dict(recipients=['anne@example.org'])
        agent = PersonalizedDeliveryTester()
        refused = agent.deliver(self.mlist, self.msg, msgdata)

        self.assertEqual(len(refused), 0)
        self.assertEqual(len(agent.deliveries), 1)

        out_msg = agent.deliveries[0][1]
        out_wrapped = PGPWrapper(out_msg)
        self.assertTrue(out_wrapped.is_encrypted())

        decrypted = out_wrapped.copy().decrypt(self.list_key)
        self.assertFalse(decrypted.is_signed())

        decrypted = out_wrapped.copy().decrypt(self.anne_key)
        self.assertFalse(decrypted.is_signed())

    def test_sign(self):
        with transaction():
            self.pgp_list.sign_outgoing = True
            self.pgp_list.encrypt_outgoing = False

        msgdata = dict(recipients=['anne@example.org'])
        agent = PersonalizedDeliveryTester()
        refused = agent.deliver(self.mlist, self.msg, msgdata)

        self.assertEqual(len(refused), 0)
        self.assertEqual(len(agent.deliveries), 1)

        out_msg = agent.deliveries[0][1]
        wrapped = PGPWrapper(out_msg)
        self.assertTrue(wrapped.is_signed())
        self.assertTrue(verifies(wrapped.verify(self.list_key.pubkey)))

    def test_none(self):
        with transaction():
            self.pgp_list.sign_outgoing = False
            self.pgp_list.encrypt_outgoing = False

        msgdata = dict(recipients=['anne@example.org'])
        agent = PersonalizedDeliveryTester()
        refused = agent.deliver(self.mlist, self.msg, msgdata)

        self.assertEqual(len(refused), 0)
        self.assertEqual(len(agent.deliveries), 1)

        out_msg = agent.deliveries[0][1]
        wrapped = PGPWrapper(out_msg)
        self.assertFalse(wrapped.is_signed())
        self.assertFalse(wrapped.is_encrypted())

    def test_no_pgp_list(self):
        ordinary_list = create_list('ordinary@example.com')
        msgdata = dict(recipients=['anne@example.org'])
        agent = PersonalizedDeliveryTester()
        refused = agent.deliver(ordinary_list, self.msg, msgdata)

        self.assertEqual(len(refused), 0)
        self.assertEqual(len(agent.deliveries), 1)

    def test_no_pgp_address(self):
        msgdata = dict(recipients=['someone@example.org'])
        agent = PGPPersonalizedDelivery()
        refused = agent.deliver(self.mlist, self.msg, msgdata)

        self.assertEqual(len(refused), 1)

    def test_no_key(self):
        with transaction():
            self.pgp_anne.key = None
        msgdata = dict(recipients=['anne@example.org'])
        agent = PGPPersonalizedDelivery()
        refused = agent.deliver(self.mlist, self.msg, msgdata)

        self.assertEqual(len(refused), 1)
