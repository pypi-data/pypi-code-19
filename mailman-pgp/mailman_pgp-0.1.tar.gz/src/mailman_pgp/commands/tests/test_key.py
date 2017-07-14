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
from mailman.email.message import Message
from mailman.interfaces.subscriptions import ISubscriptionManager
from mailman.interfaces.usermanager import IUserManager
from mailman.runners.command import CommandRunner
from mailman.testing.helpers import get_queue_messages, make_testable_runner
from mailman.utilities.datetime import now
from public import public
from zope.component import getUtility

from mailman_pgp.config import mm_config
from mailman_pgp.database import transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.mime import MIMEWrapper
from mailman_pgp.pgp.tests.base import load_key
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.workflows.base import CONFIRM_REQUEST
from mailman_pgp.workflows.key_change import CHANGE_CONFIRM_REQUEST
from mailman_pgp.workflows.subscription import OpenSubscriptionPolicy


def _create_plain(from_hdr, to_hdr, subject_hdr, payload):
    message = Message()
    message['From'] = from_hdr
    message['To'] = to_hdr
    message['Subject'] = subject_hdr
    message.set_payload(payload)
    return message


def _create_mixed(from_hdr, to_hdr, subject_hdr):
    message = Message()
    message['From'] = from_hdr
    message['To'] = to_hdr
    message['Subject'] = subject_hdr
    message.set_type('multipart/mixed')
    return message


@public
class TestPreDispatch(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        self.mlist = create_list('test@example.com')

    def test_no_arguments(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key', '')

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('No sub-command specified', results_msg.get_payload())

    def test_wrong_subcommand(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key wrooooooong', '')

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('Wrong sub-command specified', results_msg.get_payload())

    def test_no_pgp_list(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key set', '')

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn("This mailing list doesn't have pgp enabled.",
                      results_msg.get_payload())


@public
class TestPreSubscription(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        self.mlist = create_list('test@example.com', style_name='pgp-default')
        self.pgp_list = PGPMailingList.for_list(self.mlist)
        self.pgp_list.key = load_key('ecc_p256.priv.asc')

        self.bart_key = load_key('rsa_1024.priv.asc')
        self.anne_key = load_key('ecc_p256.priv.asc')

    def test_set(self):
        self.mlist.subscription_policy = OpenSubscriptionPolicy
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        bart.verified_on = now()
        token, token_owner, member = ISubscriptionManager(self.mlist).register(
                bart)

        get_queue_messages('virgin')

        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'Re: key set {}'.format(token))
        wrapped_set_message = MIMEWrapper(set_message)
        set_message = wrapped_set_message.attach_key(self.bart_key.pubkey)

        mm_config.switchboards['command'].enqueue(set_message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()

        pgp_address = PGPAddress.for_address(bart)
        self.assertIsNotNone(pgp_address)
        self.assertEqual(pgp_address.key.fingerprint,
                         self.bart_key.fingerprint)
        self.assertFalse(pgp_address.key_confirmed)

        items = get_queue_messages('virgin', expected_count=2)
        if items[0].msg['Subject'] == 'The results of your email commands':
            results = items[0].msg
            confirm_request = items[1].msg
        else:
            results = items[1].msg
            confirm_request = items[0].msg

        self.assertIn('Key succesfully set.', results.get_payload())
        self.assertIn('Key fingerprint: {}'.format(self.bart_key.fingerprint),
                      results.get_payload())

        confirm_wrapped = PGPWrapper(confirm_request)
        self.assertTrue(confirm_wrapped.is_encrypted())

    def test_set_encrypted(self):
        self.mlist.subscription_policy = OpenSubscriptionPolicy
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        bart.verified_on = now()
        token, token_owner, member = ISubscriptionManager(self.mlist).register(
                bart)

        get_queue_messages('virgin')

        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'Re: key set {}'.format(token))
        wrapped_set_message = MIMEWrapper(set_message)
        set_message = wrapped_set_message.attach_key(self.bart_key.pubkey)
        wrapped_set_message = MIMEWrapper(set_message)
        set_message = wrapped_set_message.encrypt(self.pgp_list.pubkey,
                                                  self.bart_key.pubkey)

        mm_config.switchboards['command'].enqueue(set_message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()

        pgp_address = PGPAddress.for_address(bart)
        self.assertIsNotNone(pgp_address)
        self.assertEqual(pgp_address.key.fingerprint,
                         self.bart_key.fingerprint)
        self.assertFalse(pgp_address.key_confirmed)

        items = get_queue_messages('virgin', expected_count=2)
        if items[0].msg['Subject'] == 'The results of your email commands':
            results = items[0].msg
            confirm_request = items[1].msg
        else:
            results = items[1].msg
            confirm_request = items[0].msg

        self.assertIn('Key succesfully set.', results.get_payload())
        self.assertIn('Key fingerprint: {}'.format(self.bart_key.fingerprint),
                      results.get_payload())

        confirm_wrapped = PGPWrapper(confirm_request)
        self.assertTrue(confirm_wrapped.is_encrypted())

    def test_set_no_token(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key set', '')

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('Missing token.', results_msg.get_payload())

    def test_set_no_key(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key set token', '')

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('No keys attached? Send a key.',
                      results_msg.get_payload())

    def test_set_multiple_keys(self):
        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'Re: key set token')
        wrapped_set_message = MIMEWrapper(set_message)
        set_message = wrapped_set_message.attach_key(self.bart_key.pubkey)
        wrapped_set_message = MIMEWrapper(set_message)
        set_message = wrapped_set_message.attach_key(self.anne_key.pubkey)

        mm_config.switchboards['command'].enqueue(set_message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('More than one key! Send only one key.',
                      results_msg.get_payload())

    def test_set_no_email(self):
        message = _create_mixed('', 'test@example.com', 'key set token')
        wrapped_message = MIMEWrapper(message)
        message = wrapped_message.attach_key(self.bart_key.pubkey)

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('No email to subscribe with.', results_msg.get_payload())

    def test_set_no_address(self):
        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'key set token')
        wrapped_set_message = MIMEWrapper(set_message)
        set_message = wrapped_set_message.attach_key(self.bart_key.pubkey)

        mm_config.switchboards['command'].enqueue(set_message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('No adddress to subscribe with.',
                      results_msg.get_payload())

    def test_set_no_pgp_address(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        bart.verified_on = now()

        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'key set token')
        wrapped_set_message = MIMEWrapper(set_message)
        set_message = wrapped_set_message.attach_key(self.bart_key.pubkey)

        mm_config.switchboards['command'].enqueue(set_message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('A pgp enabled address not found.',
                      results_msg.get_payload())

    def test_set_wrong_token(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        bart.verified_on = now()

        with transaction() as t:
            pgp_address = PGPAddress(bart)
            t.add(pgp_address)

        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'key set token')
        wrapped_set_message = MIMEWrapper(set_message)
        set_message = wrapped_set_message.attach_key(self.bart_key.pubkey)

        mm_config.switchboards['command'].enqueue(set_message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('Wrong token.', results_msg.get_payload())

    def test_confirm(self):
        self.mlist.subscription_policy = OpenSubscriptionPolicy
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        bart.verified_on = now()

        token, token_owner, member = ISubscriptionManager(self.mlist).register(
                bart, pubkey=self.bart_key.pubkey)

        get_queue_messages('virgin')

        message = _create_plain('bart@example.com', 'test@example.com',
                                'Re: key confirm {}'.format(token),
                                CONFIRM_REQUEST.format(
                                        self.bart_key.fingerprint,
                                        token))
        wrapped_message = MIMEWrapper(message)
        message = wrapped_message.sign(self.bart_key)

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()

        pgp_address = PGPAddress.for_address(bart)
        self.assertTrue(pgp_address.key_confirmed)
        self.assertTrue(self.mlist.is_subscribed(bart))

    def test_confirm_encrypted(self):
        self.mlist.subscription_policy = OpenSubscriptionPolicy
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        bart.verified_on = now()

        token, token_owner, member = ISubscriptionManager(self.mlist).register(
                bart, pubkey=self.bart_key.pubkey)

        get_queue_messages('virgin')

        message = _create_plain('bart@example.com', 'test@example.com',
                                'Re: key confirm {}'.format(token),
                                CONFIRM_REQUEST.format(
                                        self.bart_key.fingerprint,
                                        token))
        wrapped_message = MIMEWrapper(message)
        message = wrapped_message.sign_encrypt(self.bart_key,
                                               self.pgp_list.pubkey,
                                               self.bart_key.pubkey)

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')

        make_testable_runner(CommandRunner, 'command').run()

        pgp_address = PGPAddress.for_address(bart)
        self.assertTrue(pgp_address.key_confirmed)
        self.assertTrue(self.mlist.is_subscribed(bart))

    def test_confirm_no_token(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key confirm', '')

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('Missing token.', results_msg.get_payload())

    def test_confirm_no_email(self):
        message = _create_plain('', 'test@example.com',
                                'key confirm token', '')

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('No email to subscribe with.', results_msg.get_payload())

    def test_confirm_no_pgp_address(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key confirm token', '')

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('A pgp enabled address not found.',
                      results_msg.get_payload())

    def test_confirm_no_key(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            t.add(pgp_address)

        message = _create_plain('bart@example.com', 'test@example.com',
                                'Re: key confirm token',
                                CONFIRM_REQUEST.format(
                                        self.bart_key.fingerprint,
                                        'token'))
        wrapped_message = MIMEWrapper(message)
        message = wrapped_message.sign(self.bart_key)

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('No key set.', results_msg.get_payload())

    def test_confirm_not_signed(self):
        self.mlist.subscription_policy = OpenSubscriptionPolicy
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        bart.verified_on = now()

        token, token_owner, member = ISubscriptionManager(self.mlist).register(
                bart, pubkey=self.bart_key.pubkey)

        get_queue_messages('virgin')

        message = _create_plain('bart@example.com', 'test@example.com',
                                'Re: key confirm {}'.format(token),
                                CONFIRM_REQUEST.format(
                                        self.bart_key.fingerprint,
                                        token))

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()

        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('Message not signed, ignoring.',
                      results_msg.get_payload())

    def test_confirm_invalid_sig(self):
        self.mlist.subscription_policy = OpenSubscriptionPolicy
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        bart.verified_on = now()

        token, token_owner, member = ISubscriptionManager(self.mlist).register(
                bart, pubkey=self.bart_key.pubkey)

        get_queue_messages('virgin')

        message = _create_plain('bart@example.com', 'test@example.com',
                                'Re: key confirm {}'.format(token),
                                CONFIRM_REQUEST.format(
                                        self.bart_key.fingerprint,
                                        token))
        wrapped_message = MIMEWrapper(message)
        message = wrapped_message.sign(self.bart_key)
        message.get_payload(0).set_payload(
                'Something that was definitely not signed.')

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()

        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('Message failed to verify.',
                      results_msg.get_payload())

    def test_confirm_wrong_token(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        bart.verified_on = now()

        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            t.add(pgp_address)

        message = _create_plain('bart@example.com', 'test@example.com',
                                'Re: key confirm token',
                                CONFIRM_REQUEST.format(
                                        self.bart_key.fingerprint,
                                        'token'))
        wrapped_message = MIMEWrapper(message)
        message = wrapped_message.sign(self.bart_key)

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()

        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('Wrong token.', results_msg.get_payload())

    def test_confirm_no_signed_statement(self):
        self.mlist.subscription_policy = OpenSubscriptionPolicy
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        bart.verified_on = now()

        token, token_owner, member = ISubscriptionManager(self.mlist).register(
                bart, pubkey=self.bart_key.pubkey)

        get_queue_messages('virgin')

        message = _create_plain('bart@example.com', 'test@example.com',
                                'Re: key confirm {}'.format(token),
                                'Some text, that definitely does not'
                                'contain the required/expected statement.')
        wrapped_message = MIMEWrapper(message)
        message = wrapped_message.sign(self.bart_key)

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()

        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn("Message doesn't contain the expected statement.",
                      results_msg.get_payload())


@public
class TestAfterSubscription(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        self.mlist = create_list('test@example.com', style_name='pgp-default')
        self.pgp_list = PGPMailingList.for_list(self.mlist)
        self.pgp_list.key = load_key('ecc_p256.priv.asc')

        self.bart_key = load_key('rsa_1024.priv.asc')
        self.bart_new_key = load_key('ecc_p256.priv.asc')

    def test_change(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')

        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key change')
        wrapped_message = MIMEWrapper(message)
        message = wrapped_message.attach_key(self.bart_new_key.pubkey)

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()

        items = get_queue_messages('virgin', expected_count=2)
        if items[0].msg['Subject'] == 'The results of your email commands':
            results = items[0].msg
            confirm_request = items[1].msg
        else:
            results = items[1].msg
            confirm_request = items[0].msg

        self.assertIn('Key change request received.', results.get_payload())

        confirm_wrapped = PGPWrapper(confirm_request)
        self.assertTrue(confirm_wrapped.is_encrypted())
        decrypted = confirm_wrapped.decrypt(self.bart_new_key)
        self.assertIn('key confirm', decrypted['subject'])

    def test_change_confirm(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')

        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key change')
        wrapped_message = MIMEWrapper(message)
        message = wrapped_message.attach_key(self.bart_new_key.pubkey)

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()

        items = get_queue_messages('virgin', expected_count=2)
        if items[0].msg['Subject'] == 'The results of your email commands':
            confirm_request = items[1].msg
        else:
            confirm_request = items[0].msg
        request_wrapped = PGPWrapper(confirm_request)
        decrypted = request_wrapped.decrypt(self.bart_new_key)

        subj = decrypted['subject']
        token = subj.split(' ')[-1]

        confirm_message = _create_plain('bart@example.com', 'test@example.com',
                                        decrypted['subject'],
                                        CHANGE_CONFIRM_REQUEST.format(
                                                self.bart_new_key.fingerprint,
                                                token))
        wrapped_confirm = MIMEWrapper(confirm_message)
        confirm = wrapped_confirm.sign(self.bart_key)

        mm_config.switchboards['command'].enqueue(confirm,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()

        pgp_address = PGPAddress.for_address(bart)
        self.assertEqual(pgp_address.key_fingerprint,
                         self.bart_new_key.fingerprint)
        self.assertTrue(pgp_address.key_confirmed)

    def test_change_extra_arg(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key change extra arguments', '')
        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()

        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('Extraneous argument/s: extra,arguments',
                      results_msg.get_payload())

    def test_change_no_key(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key change', '')

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('No keys attached? Send a key.',
                      results_msg.get_payload())

    def test_change_multiple_keys(self):
        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'key change')

        wrapped_set_message = MIMEWrapper(set_message)
        set_message = wrapped_set_message.attach_key(self.bart_key.pubkey)
        wrapped_set_message = MIMEWrapper(set_message)
        set_message = wrapped_set_message.attach_key(self.bart_new_key.pubkey)

        mm_config.switchboards['command'].enqueue(set_message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('More than one key! Send only one key.',
                      results_msg.get_payload())

    def test_change_no_email(self):
        message = _create_mixed('', 'test@example.com', 'key change')
        wrapped_message = MIMEWrapper(message)
        message = wrapped_message.attach_key(self.bart_key.pubkey)

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('No email to change key of.', results_msg.get_payload())

    def test_change_no_pgp_address(self):
        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key change')
        wrapped_message = MIMEWrapper(message)
        message = wrapped_message.attach_key(self.bart_key.pubkey)

        mm_config.switchboards['command'].enqueue(message,
                                                  listid='test.example.com')
        make_testable_runner(CommandRunner, 'command').run()
        items = get_queue_messages('virgin', expected_count=1)
        results_msg = items[0].msg

        self.assertIn('A pgp enabled address not found.',
                      results_msg.get_payload())
