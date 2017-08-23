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
import time
import unittest
from datetime import timedelta

from mailman.app.lifecycle import create_list
from mailman.email.message import Message
from mailman.interfaces.action import Action
from mailman.interfaces.chain import AcceptEvent
from mailman.interfaces.member import MemberRole
from mailman.interfaces.usermanager import IUserManager
from mailman.testing.helpers import (set_preferred,
                                     specialized_message_from_string as mfs)
from zope.component import getUtility
from zope.event import notify

from mailman_pgp.chains.default import PGPChain
from mailman_pgp.config import mm_config
from mailman_pgp.database import mm_transaction, transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.model.sighash import PGPSigHash
from mailman_pgp.pgp.inline import InlineWrapper
from mailman_pgp.pgp.mime import MIMEWrapper
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.rules.signature import Signature
from mailman_pgp.testing.config import patch_config
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.testing.pgp import load_key, load_message
from mailman_pgp.utils.pgp import hashes


class TestPGPSignatureRule(unittest.TestCase):
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

        self.sender_key = load_key('rsa_1024.priv.asc')
        with transaction() as t:
            self.pgp_sender = PGPAddress(self.sender.preferred_address)
            self.pgp_sender.key = self.sender_key.pubkey
            self.pgp_sender.key_confirmed = True
            t.add(self.pgp_sender)

        self.msg_clear = load_message('clear.eml')
        self.msg_inline_signed = load_message('inline_signed.eml')
        self.msg_mime_signed = load_message('mime_signed.eml')
        self.msg_inline_signed_invalid = load_message(
                'inline_cleartext_signed_invalid.eml')
        self.msg_mime_signed_invalid = load_message(
                'mime_signed_invalid.eml')

    def assertAction(self, msgdata, action, reasons):
        self.assertEqual(msgdata['pgp_action'], action.name)
        self.assertListEqual(msgdata['moderation_reasons'], reasons)

    def test_has_rule(self):
        self.assertIn(Signature.name, mm_config.rules.keys())

    def test_no_pgp_list(self):
        with mm_transaction():
            ordinary_list = create_list('odrinary@example.com')
        msg = mfs("""\
From: anne@example.com
To: ordinary@example.com

""")

        matches = self.rule.check(ordinary_list, msg, {})
        self.assertFalse(matches)

    def test_no_address(self):
        with transaction():
            self.pgp_list.unsigned_msg_action = Action.defer
        msg = mfs("""\
From: anne@example.com
To: test@example.com

""")
        matches = self.rule.check(self.mlist, msg, {})
        self.assertFalse(matches)

    def test_no_key(self):
        with transaction():
            self.pgp_sender.key = None

        msgdata = {}
        matches = self.rule.check(self.mlist, self.msg_mime_signed, msgdata)
        self.assertTrue(matches)
        self.assertAction(msgdata, Action.reject, [
            'No key set for address {}.'.format(
                    self.pgp_sender.address.original_email)])

    def test_key_not_confirmed(self):
        with transaction():
            self.pgp_sender.key_confirmed = False

        msgdata = {}
        matches = self.rule.check(self.mlist, self.msg_mime_signed, msgdata)
        self.assertTrue(matches)
        self.assertAction(msgdata, Action.reject, ['Key not confirmed.'])

    def test_unsigned_action(self):
        with transaction():
            self.pgp_list.unsigned_msg_action = Action.hold
            self.pgp_list.inline_pgp_action = Action.defer
            self.pgp_list.expired_sig_action = Action.defer
            self.pgp_list.invalid_sig_action = Action.defer
            self.pgp_list.revoked_sig_action = Action.defer
            self.pgp_list.duplicate_sig_action = Action.defer

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
            self.pgp_list.duplicate_sig_action = Action.defer

        msgdata = {}
        matches = self.rule.check(self.mlist, self.msg_inline_signed, msgdata)
        self.assertTrue(matches)
        self.assertAction(msgdata, Action.hold, ['Inline PGP is not allowed.'])

        matches = self.rule.check(self.mlist, self.msg_mime_signed, msgdata)
        self.assertFalse(matches)

    def test_expired_sig_action(self):
        with transaction():
            self.pgp_list.unsigned_msg_action = Action.defer
            self.pgp_list.inline_pgp_action = Action.defer
            self.pgp_list.expired_sig_action = Action.hold
            self.pgp_list.invalid_sig_action = Action.defer
            self.pgp_list.revoked_sig_action = Action.defer
            self.pgp_list.duplicate_sig_action = Action.defer

        msgdata = {}
        wrapped = MIMEWrapper(self.msg_clear, True)
        msg = wrapped.sign(self.sender_key, expires=timedelta(seconds=1)).msg
        time.sleep(2)
        matches = self.rule.check(self.mlist, msg, msgdata)

        self.assertTrue(matches)
        self.assertAction(msgdata, Action.hold, ['Signature is expired.'])

        msgdata = {}
        wrapped = InlineWrapper(self.msg_clear, True)
        msg = wrapped.sign(self.sender_key, expires=timedelta(seconds=1)).msg
        time.sleep(2)
        matches = self.rule.check(self.mlist, msg, msgdata)

        # TODO: test when the key is expired

        self.assertTrue(matches)
        self.assertAction(msgdata, Action.hold, ['Signature is expired.'])

    def test_revoked_sig_action(self):
        with transaction():
            self.pgp_list.unsigned_msg_action = Action.defer
            self.pgp_list.inline_pgp_action = Action.defer
            self.pgp_list.expired_sig_action = Action.defer
            self.pgp_list.revoked_sig_action = Action.hold
            self.pgp_list.invalid_sig_action = Action.defer
            self.pgp_list.duplicate_sig_action = Action.defer

            rsig = self.sender_key.revoke(self.pgp_sender.key)
            self.pgp_sender.key |= rsig

        msgdata = {}
        wrapped = MIMEWrapper(self.msg_clear)
        msg = wrapped.sign(self.sender_key).msg
        matches = self.rule.check(self.mlist, msg, msgdata)

        self.assertTrue(matches)
        self.assertAction(msgdata, Action.hold,
                          ['Signature is made by a revoked key.'])

    def test_invalid_sig_action(self):
        with transaction():
            self.pgp_list.unsigned_msg_action = Action.defer
            self.pgp_list.inline_pgp_action = Action.defer
            self.pgp_list.expired_sig_action = Action.defer
            self.pgp_list.invalid_sig_action = Action.hold
            self.pgp_list.revoked_sig_action = Action.defer
            self.pgp_list.duplicate_sig_action = Action.defer

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

    def test_duplicate_sig_action(self):
        with transaction() as t:
            self.pgp_list.unsigned_msg_action = Action.defer
            self.pgp_list.inline_pgp_action = Action.defer
            self.pgp_list.expired_sig_action = Action.defer
            self.pgp_list.invalid_sig_action = Action.defer
            self.pgp_list.revoked_sig_action = Action.defer
            self.pgp_list.duplicate_sig_action = Action.hold

            wrapped = PGPWrapper(self.msg_mime_signed)
            sig_hashes = set(hashes(wrapped.verify(self.sender_key.pubkey)))
            wrapped = PGPWrapper(self.msg_inline_signed)
            sig_hashes |= set(hashes(wrapped.verify(self.sender_key.pubkey)))
            for hash in sig_hashes:
                sig_hash = PGPSigHash()
                sig_hash.hash = hash
                sig_hash.fingerprint = self.sender_key.pubkey.fingerprint
                t.add(sig_hash)

        msgdata = {}
        matches = self.rule.check(self.mlist, self.msg_mime_signed, msgdata)
        self.assertTrue(matches)
        self.assertAction(msgdata, Action.hold, ['Signature duplicate.'])

        msgdata = {}
        matches = self.rule.check(self.mlist, self.msg_inline_signed, msgdata)
        self.assertTrue(matches)
        self.assertAction(msgdata, Action.hold, ['Signature duplicate.'])


class TestPostingEvent(unittest.TestCase):
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

        self.sender_key = load_key('rsa_1024.priv.asc')
        with transaction() as t:
            self.pgp_sender = PGPAddress(self.sender.preferred_address)
            self.pgp_sender.key = self.sender_key.pubkey
            self.pgp_sender.key_confirmed = True
            t.add(self.pgp_sender)

    def test_sighashes_added(self):
        msg = load_message('mime_signed.eml')
        wrapped = PGPWrapper(msg)
        sighashes = set(hashes(wrapped.verify(self.sender_key)))
        msgdata = dict(pgp_sig_hashes=sighashes)
        notify(AcceptEvent(self.mlist, msg, msgdata,
                           mm_config.chains[PGPChain.name]))

        for hash in sighashes:
            sig_hash = PGPSigHash.query().filter_by(hash=hash).one()
            self.assertIsNotNone(sig_hash)
            self.assertEqual(sig_hash.fingerprint, self.sender_key.fingerprint)

    @patch_config('misc', 'collect_sig_hashes', 'no')
    def test_no_collect(self):
        msg = load_message('mime_signed.eml')
        wrapped = PGPWrapper(msg)
        sighashes = set(hashes(wrapped.verify(self.sender_key)))
        msgdata = dict(pgp_sig_hashes=sighashes)
        notify(AcceptEvent(self.mlist, msg, msgdata,
                           mm_config.chains[PGPChain.name]))

        self.assertEqual(0, len(PGPSigHash.query().all()))

    def test_no_pgp_list(self):
        with mm_transaction():
            mlist = create_list('ordinary@example.com')
        notify(AcceptEvent(mlist, Message(), dict(),
                           mm_config.chains[PGPChain.name]))

    def test_no_pgp_address(self):
        msg = mfs("""\
From: anne@example.com
To: test@example.com
Subject: something

Some text.
""")
        notify(AcceptEvent(self.mlist, msg, dict(),
                           mm_config.chains[PGPChain.name]))
