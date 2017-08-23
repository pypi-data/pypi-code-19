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
import unittest
from copy import deepcopy

from mailman.app.lifecycle import create_list
from mailman.interfaces.usermanager import IUserManager
from zope.component import getUtility

from mailman_pgp.config import mm_config
from mailman_pgp.database import mm_transaction, transaction
from mailman_pgp.handlers.signature_strip import SignatureStrip
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.inline import InlineWrapper
from mailman_pgp.pgp.mime import MIMEWrapper
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.testing.pgp import load_key, load_message


class TestSignatureStripHandler(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        self.handler = SignatureStrip()

        user_manager = getUtility(IUserManager)
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')
            self.sender = user_manager.create_address('anne@example.com')

        self.pgp_list = PGPMailingList.for_list(self.mlist)
        with transaction():
            self.pgp_list.strip_original_sig = True

        self.sender_key = load_key('rsa_1024.priv.asc')
        with transaction() as t:
            self.pgp_sender = PGPAddress(self.sender)
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

    def test_has_handler(self):
        self.assertIn(SignatureStrip.name, mm_config.handlers.keys())

    def test_no_list(self):
        with mm_transaction():
            ordinary = create_list('ordinary@example.com')

        self.handler.process(ordinary, self.msg_clear, {})

    def test_no_strip(self):
        with transaction():
            self.pgp_list.strip_original_sig = False

        msg = deepcopy(self.msg_mime_signed)
        self.handler.process(self.mlist, msg, {})
        self.assertTrue(MIMEWrapper(msg).is_signed())

        msg = deepcopy(self.msg_inline_signed)
        self.handler.process(self.mlist, msg, {})
        self.assertTrue(InlineWrapper(msg).is_signed())

    def test_strip(self):
        msg = deepcopy(self.msg_mime_signed)
        self.handler.process(self.mlist, msg, {})
        self.assertFalse(MIMEWrapper(msg).is_signed())
        self.assertFalse(MIMEWrapper(msg).has_signature())

        msg = deepcopy(self.msg_inline_signed)
        self.handler.process(self.mlist, msg, {})
        self.assertFalse(InlineWrapper(msg).is_signed())
        self.assertFalse(InlineWrapper(msg).has_signature())
