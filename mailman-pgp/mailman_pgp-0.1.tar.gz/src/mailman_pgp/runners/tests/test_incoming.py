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
from mailman.testing.helpers import (get_queue_messages, make_testable_runner,
                                     set_preferred,
                                     specialized_message_from_string as mfs)
from zope.component import getUtility

from mailman_pgp.config import mm_config
from mailman_pgp.database import mm_transaction, transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.tests.base import load_key, load_message
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.runners.incoming import IncomingRunner
from mailman_pgp.testing.layers import PGPConfigLayer


class TestIncoming(TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        user_manager = getUtility(IUserManager)
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')
            self.sender = user_manager.create_user('RSA-1024b@example.org')
            set_preferred(self.sender)
            self.mlist.subscribe(self.sender, MemberRole.member)

        self.list_key = load_key('ecc_p256.priv.asc')
        self.pgp_list = PGPMailingList.for_list(self.mlist)
        self.pgp_list.key = self.list_key

        self.sender_key = load_key('rsa_1024.priv.asc')
        with transaction() as t:
            self.pgp_sender = PGPAddress(self.sender.preferred_address)
            self.pgp_sender.key = self.sender_key.pubkey
            t.add(self.pgp_sender)

        self.msg_clear = load_message('clear.eml')

        self.runner = make_testable_runner(IncomingRunner, 'in')

    def test_pass_default(self):
        with mm_transaction():
            create_list('ordinary@example.com')

        msg = mfs("""\
From: anne@example.com
To: ordinary@example.com

""")

        msgdata = dict(listid='ordinary.example.com')
        mm_config.switchboards['in'].enqueue(msg, msgdata)
        self.runner.run()
        items = get_queue_messages('in_default', expected_count=1)
        self.assertEqual(items[0].msg.sender, 'anne@example.com')

    def test_no_key(self):
        with mm_transaction():
            create_list('no-key@example.com',
                        style_name='pgp-default')
        msg = mfs("""\
From: RSA-1024b@example.org
To: no-key@example.com

Some text.
""")
        wrapped = PGPWrapper(msg)
        encrypted = wrapped.encrypt(self.pgp_list.pubkey)

        msgdata = dict(listid='no-key.example.com')
        mm_config.switchboards['in'].enqueue(encrypted, msgdata)
        runner = make_testable_runner(IncomingRunner, 'in',
                                      lambda runner: True)
        runner.run()
        # Expect the message still there. Waiting for list key.
        get_queue_messages('in', expected_count=1)

    def test_nonencrypted_action(self):
        with transaction():
            self.pgp_list.nonencrypted_msg_action = Action.hold

        msgdata = dict(listid='test.example.com')
        mm_config.switchboards['in'].enqueue(self.msg_clear, msgdata)
        self.runner.run()
        items = get_queue_messages('in_default', expected_count=1)
        self.assertEqual(items[0].msgdata['moderation_action'],
                         Action.hold.name)
        self.assertEqual(items[0].msgdata['moderation_sender'],
                         self.msg_clear.sender)
        self.assertEqual(items[0].msgdata['moderation_reason'],
                         'Message was not encrypted.')
        self.assertTrue(items[0].msgdata['pgp_moderate'])

        with transaction():
            self.pgp_list.nonencrypted_msg_action = Action.defer

        msgdata = dict(listid='test.example.com')
        mm_config.switchboards['in'].enqueue(self.msg_clear, msgdata)
        self.runner.run()
        get_queue_messages('in_default', expected_count=1)

    def test_decrypt(self):
        payload = 'Some encrypted text.'
        msg = mfs("""\
From: RSA-1024b@example.org
To: test@example.com

{}
""".format(str(payload)))
        wrapped = PGPWrapper(msg)
        encrypted = wrapped.encrypt(self.pgp_list.pubkey)

        msgdata = dict(listid='test.example.com')
        mm_config.switchboards['in'].enqueue(encrypted,
                                             msgdata)
        self.runner.run()
        items = get_queue_messages('in_default', expected_count=1)
        out_msg = items[0].msg
        self.assertEqual(out_msg.get_payload(), msg.get_payload())

    def test_decrypt_combined(self):
        payload = 'Some signed and encrypted text.'
        msg = mfs("""\
From: RSA-1024b@example.org
To: test@example.com

{}
""".format(str(payload)))
        wrapped = PGPWrapper(msg)
        encrypted_signed = wrapped.sign_encrypt(self.sender_key,
                                                self.pgp_list.pubkey,
                                                self.pgp_sender.key)

        msgdata = dict(listid='test.example.com')
        mm_config.switchboards['in'].enqueue(encrypted_signed,
                                             msgdata)
        self.runner.run()
        items = get_queue_messages('in_default', expected_count=1)
        out_msg = items[0].msg
        out_wrapped = PGPWrapper(out_msg)
        self.assertTrue(out_wrapped.is_signed())
        self.assertTrue(out_wrapped.verifies(self.pgp_sender.key))
