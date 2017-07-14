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

from mailman.app.lifecycle import create_list
from mailman.interfaces.action import Action
from mailman.interfaces.member import MemberRole
from mailman.interfaces.usermanager import IUserManager
from mailman.testing.helpers import (set_preferred,
                                     specialized_message_from_string as mfs)
from zope.component import getUtility

from mailman_pgp.config import mm_config
from mailman_pgp.database import mm_transaction, transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.tests.base import load_key, load_message
from mailman_pgp.rules.signature import Signature
from mailman_pgp.testing.layers import PGPConfigLayer


class TestSignatureRule(TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        self.rule = Signature()

        user_manager = getUtility(IUserManager)
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')
            self.sender = user_manager.create_user('RSA-1024b@example.org')
            set_preferred(self.sender)
            self.mlist.subscribe(self.sender, MemberRole.member)

        self.pgp_list = PGPMailingList.for_list(self.mlist)

        sender_key = load_key('rsa_1024.pub.asc')
        with transaction() as t:
            self.pgp_sender = PGPAddress(self.sender.preferred_address)
            self.pgp_sender.key = sender_key
            t.add(self.pgp_sender)

        self.msg_clear = load_message('clear.eml')
        self.msg_inline_signed = load_message('inline_signed.eml')
        self.msg_mime_signed = load_message('mime_signed.eml')
        self.msg_inline_signed_invalid = load_message(
                'inline_cleartext_signed_invalid.eml')
        self.msg_mime_signed_invalid = load_message(
                'mime_signed_invalid.eml')

    def test_has_rule(self):
        self.assertIn(Signature.name, mm_config.rules.keys())

    def test_no_pgp_list(self):
        with mm_transaction():
            ordinary_list = create_list('odrinary@example.com')
        msg = mfs("""\
From: anne@example.com
To: ordinary@example.com

""")

        with self.assertRaises(ValueError):
            self.rule.check(ordinary_list, msg, {})

    def test_no_address(self):
        with transaction():
            self.pgp_list.unsigned_msg_action = Action.defer
        msg = mfs("""\
From: anne@example.com
To: test@example.com

""")
        with self.assertRaises(ValueError):
            self.rule.check(self.mlist, msg, {})

    def test_no_key(self):
        with transaction():
            self.pgp_sender.key = None

        msgdata = {}
        with self.assertRaises(ValueError):
            self.rule.check(self.mlist, self.msg_mime_signed, msgdata)

    def assertAction(self, msgdata, action, reasons):
        self.assertEqual(msgdata['moderation_action'], action.name)
        self.assertListEqual(msgdata['moderation_reasons'], reasons)

    def test_unsigned_action(self):
        with transaction():
            self.pgp_list.unsigned_msg_action = Action.hold
            self.pgp_list.inline_pgp_action = Action.defer
            self.pgp_list.expired_sig_action = Action.defer
            self.pgp_list.invalid_sig_action = Action.defer
            self.pgp_list.revoked_sig_action = Action.defer

        msgdata = {}
        matches = self.rule.check(self.mlist, self.msg_clear, msgdata)
        self.assertTrue(matches)
        self.assertAction(msgdata, Action.hold, ['The message is unsigned.'])

        matches = self.rule.check(self.mlist, self.msg_inline_signed, msgdata)
        self.assertFalse(matches)

        matches = self.rule.check(self.mlist, self.msg_mime_signed, msgdata)
        self.assertFalse(matches)

    def test_inline_pgp_action(self):
        with transaction():
            self.pgp_list.unsigned_msg_action = Action.defer
            self.pgp_list.inline_pgp_action = Action.hold
            self.pgp_list.expired_sig_action = Action.defer
            self.pgp_list.invalid_sig_action = Action.defer
            self.pgp_list.revoked_sig_action = Action.defer

        msgdata = {}
        matches = self.rule.check(self.mlist, self.msg_inline_signed, msgdata)
        self.assertTrue(matches)
        self.assertAction(msgdata, Action.hold, ['Inline PGP is not allowed.'])

        matches = self.rule.check(self.mlist, self.msg_mime_signed, msgdata)
        self.assertFalse(matches)

    def test_invalid_sig_action(self):
        with transaction():
            self.pgp_list.unsigned_msg_action = Action.defer
            self.pgp_list.inline_pgp_action = Action.defer
            self.pgp_list.expired_sig_action = Action.defer
            self.pgp_list.invalid_sig_action = Action.hold
            self.pgp_list.revoked_sig_action = Action.defer

        msgdata = {}
        matches = self.rule.check(self.mlist, self.msg_inline_signed_invalid,
                                  msgdata)
        self.assertTrue(matches)
        self.assertAction(msgdata, Action.hold, ['Signature did not verify.'])

        msgdata = {}
        matches = self.rule.check(self.mlist, self.msg_mime_signed_invalid,
                                  msgdata)
        self.assertTrue(matches)
        self.assertAction(msgdata, Action.hold, ['Signature did not verify.'])
