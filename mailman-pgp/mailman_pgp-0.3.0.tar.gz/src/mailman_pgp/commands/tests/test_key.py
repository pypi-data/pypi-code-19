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
import copy
import unittest

from mailman.app.lifecycle import create_list
from mailman.email.message import Message, MultipartDigestMessage
from mailman.interfaces.member import MemberRole
from mailman.interfaces.subscriptions import ISubscriptionManager
from mailman.interfaces.usermanager import IUserManager
from mailman.runners.command import CommandRunner
from mailman.testing.helpers import get_queue_messages, make_testable_runner
from mailman.utilities.datetime import now
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm, EllipticCurveOID, HashAlgorithm, KeyFlags,
    PubKeyAlgorithm, SymmetricKeyAlgorithm)
from zope.component import getUtility

from mailman_pgp.config import mm_config
from mailman_pgp.database import mm_transaction, transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.mime import MIMEWrapper
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.testing.pgp import load_key
from mailman_pgp.workflows.key_change import CHANGE_CONFIRM_REQUEST
from mailman_pgp.workflows.key_confirm import CONFIRM_REQUEST
from mailman_pgp.workflows.subscription import OpenSubscriptionPolicy


def _create_plain(from_hdr, to_hdr, subject_hdr, payload):
    message = Message()
    message['From'] = from_hdr
    message['To'] = to_hdr
    message['Subject'] = subject_hdr
    message.set_payload(payload)
    return message


def _create_mixed(from_hdr, to_hdr, subject_hdr):
    message = MultipartDigestMessage()
    message['From'] = from_hdr
    message['To'] = to_hdr
    message['Subject'] = subject_hdr
    message.set_payload([])
    return message


def _run_message(message, expected_responses=None, list_id='test.example.com'):
    mm_config.switchboards['command'].enqueue(message, listid=list_id)
    make_testable_runner(CommandRunner, 'command').run()
    return get_queue_messages('virgin', expected_count=expected_responses)


class TestPreDispatch(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        self.mlist = create_list('test@example.com')

    def test_no_arguments(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key', '')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No sub-command specified', results_msg.get_payload())

    def test_wrong_subcommand(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key wrooooooong', '')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('Wrong sub-command specified', results_msg.get_payload())

    def test_no_pgp_list(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key set', '')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn("This mailing list doesn't have pgp enabled.",
                      results_msg.get_payload())


class TestPreSubscription(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        self.mlist = create_list('test@example.com', style_name='pgp-default')
        self.pgp_list = PGPMailingList.for_list(self.mlist)
        self.pgp_list.key = load_key('ecc_p256.priv.asc')

        self.bart_key = load_key('rsa_1024.priv.asc')
        self.anne_key = load_key('ecc_p256.priv.asc')

        self.unusable_key = PGPKey.new(PubKeyAlgorithm.ECDSA,
                                       EllipticCurveOID.SECP256K1)
        uid = PGPUID.new('Bart Person', email='bart@example.com')
        self.unusable_key.add_uid(uid,
                                  usage={KeyFlags.Certify,
                                         KeyFlags.Authentication,
                                         KeyFlags.Sign},
                                  hashes=[HashAlgorithm.SHA256,
                                          HashAlgorithm.SHA512],
                                  ciphers=[SymmetricKeyAlgorithm.AES256],
                                  compression=[CompressionAlgorithm.ZLIB]
                                  )

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
        MIMEWrapper(set_message).attach_keys(self.bart_key.pubkey)

        items = _run_message(set_message, 2)

        pgp_address = PGPAddress.for_address(bart)
        self.assertIsNotNone(pgp_address)
        self.assertEqual(pgp_address.key.fingerprint,
                         self.bart_key.fingerprint)
        self.assertFalse(pgp_address.key_confirmed)

        if (items[0].msg['Subject'] ==
                'The results of your email commands'):  # pragma: no cover
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
        MIMEWrapper(set_message).attach_keys(self.bart_key.pubkey).encrypt(
                self.pgp_list.pubkey,
                self.bart_key.pubkey)

        items = _run_message(set_message, 2)

        pgp_address = PGPAddress.for_address(bart)
        self.assertIsNotNone(pgp_address)
        self.assertEqual(pgp_address.key.fingerprint,
                         self.bart_key.fingerprint)
        self.assertFalse(pgp_address.key_confirmed)

        if (items[0].msg['Subject'] ==
                'The results of your email commands'):  # pragma: no cover
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

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('Missing token.', results_msg.get_payload())

    def test_set_no_key(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key set token', '')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No keys attached? Send a key.',
                      results_msg.get_payload())

    def test_set_multiple_keys(self):
        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'Re: key set token')
        MIMEWrapper(set_message).attach_keys(self.bart_key.pubkey).attach_keys(
                self.anne_key.pubkey)

        items = _run_message(set_message, 1)
        results_msg = items[0].msg

        self.assertIn('More than one key! Send only one key.',
                      results_msg.get_payload())

    def test_set_private_key(self):
        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'Re: key set token')
        MIMEWrapper(set_message).attach_keys(self.bart_key)

        items = _run_message(set_message, 1)
        results_msg = items[0].msg

        self.assertIn('You probably wanted to send your public key only.',
                      results_msg.get_payload())

    def test_set_no_encrypt_key(self):
        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'Re: key set token')
        MIMEWrapper(set_message).attach_keys(self.unusable_key.pubkey)

        items = _run_message(set_message, 1)
        results_msg = items[0].msg

        self.assertIn(
                'Need a key which can be used to encrypt communications.',
                results_msg.get_payload())

    def test_set_no_email(self):
        message = _create_mixed('', 'test@example.com', 'key set token')
        MIMEWrapper(message).attach_keys(self.bart_key.pubkey)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No email to subscribe with.', results_msg.get_payload())

    def test_set_no_address(self):
        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'key set token')
        MIMEWrapper(set_message).attach_keys(self.bart_key.pubkey)

        items = _run_message(set_message, 1)
        results_msg = items[0].msg

        self.assertIn('No adddress to subscribe with.',
                      results_msg.get_payload())

    def test_set_no_pgp_address(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        bart.verified_on = now()

        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'key set token')
        MIMEWrapper(set_message).attach_keys(self.bart_key.pubkey)

        items = _run_message(set_message, 1)
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
        MIMEWrapper(set_message).attach_keys(self.bart_key.pubkey)

        items = _run_message(set_message, 1)
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
        MIMEWrapper(message).sign(self.bart_key)

        _run_message(message)

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
        MIMEWrapper(message).sign_encrypt(self.bart_key,
                                          self.pgp_list.pubkey,
                                          self.bart_key.pubkey)

        _run_message(message)

        pgp_address = PGPAddress.for_address(bart)
        self.assertTrue(pgp_address.key_confirmed)
        self.assertTrue(self.mlist.is_subscribed(bart))

    def test_confirm_no_token(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key confirm', '')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('Missing token.', results_msg.get_payload())

    def test_confirm_no_email(self):
        message = _create_plain('', 'test@example.com',
                                'key confirm token', '')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No email to subscribe with.', results_msg.get_payload())

    def test_confirm_no_pgp_address(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key confirm token', '')

        items = _run_message(message, 1)
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
        MIMEWrapper(message).sign(self.bart_key)

        items = _run_message(message, 1)
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

        items = _run_message(message, 1)
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
        MIMEWrapper(message).sign(self.bart_key)
        message.get_payload(0).set_payload(
                'Something that was definitely not signed.')

        items = _run_message(message, 1)
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
        MIMEWrapper(message).sign(self.bart_key)

        items = _run_message(message, 1)
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
        MIMEWrapper(message).sign(self.bart_key)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn("Message doesn't contain the expected statement.",
                      results_msg.get_payload())


class TestAfterSubscription(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')
        with transaction():
            self.pgp_list = PGPMailingList.for_list(self.mlist)
            self.pgp_list.key = load_key('ecc_p256.priv.asc')
            self.pgp_list.key_change_workflow = 'pgp-key-change-workflow'

        self.bart_key = load_key('rsa_1024.priv.asc')
        self.bart_new_key = load_key('ecc_p256.priv.asc')

        self.unusable_key = PGPKey.new(PubKeyAlgorithm.ECDSA,
                                       EllipticCurveOID.SECP256K1)
        uid = PGPUID.new('Bart Person', email='bart@example.com')
        self.unusable_key.add_uid(uid,
                                  usage={KeyFlags.Certify,
                                         KeyFlags.Authentication,
                                         KeyFlags.Sign},
                                  hashes=[HashAlgorithm.SHA256,
                                          HashAlgorithm.SHA512],
                                  ciphers=[SymmetricKeyAlgorithm.AES256],
                                  compression=[CompressionAlgorithm.ZLIB]
                                  )

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
        MIMEWrapper(message).attach_keys(self.bart_new_key.pubkey)

        items = _run_message(message, 2)
        if (items[0].msg['Subject'] ==
                'The results of your email commands'):  # pragma: no cover
            results = items[0].msg
            confirm_request = items[1].msg
        else:
            results = items[1].msg
            confirm_request = items[0].msg

        self.assertIn('Key change request received.', results.get_payload())

        confirm_wrapped = PGPWrapper(confirm_request)
        self.assertTrue(confirm_wrapped.is_encrypted())
        decrypted = confirm_wrapped.decrypt(self.bart_new_key).msg
        self.assertIn('key confirm', str(decrypted['subject']))

    def test_change_encrypted(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')

        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key change')
        MIMEWrapper(message).attach_keys(self.bart_new_key.pubkey).encrypt(
                self.pgp_list.pubkey)

        items = _run_message(message, 2)
        if (items[0].msg['Subject'] ==
                'The results of your email commands'):  # pragma: no cover
            results = items[0].msg
            confirm_request = items[1].msg
        else:
            results = items[1].msg
            confirm_request = items[0].msg

        self.assertIn('Key change request received.', results.get_payload())

        confirm_wrapped = PGPWrapper(confirm_request)
        self.assertTrue(confirm_wrapped.is_encrypted())
        decrypted = confirm_wrapped.decrypt(self.bart_new_key).msg
        self.assertIn('key confirm', str(decrypted['subject']))

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
        MIMEWrapper(message).attach_keys(self.bart_new_key.pubkey)

        items = _run_message(message, 2)
        if (items[0].msg['Subject'] ==
                'The results of your email commands'):  # pragma: no cover
            confirm_request = items[1].msg
        else:
            confirm_request = items[0].msg
        request_wrapped = PGPWrapper(confirm_request)
        decrypted = request_wrapped.decrypt(self.bart_new_key).msg

        subj = decrypted['subject']
        token = str(subj).split(' ')[-1]

        confirm_message = _create_plain('bart@example.com', 'test@example.com',
                                        decrypted['subject'],
                                        CHANGE_CONFIRM_REQUEST.format(
                                                self.bart_new_key.fingerprint,
                                                token))
        MIMEWrapper(confirm_message).sign(self.bart_key)

        _run_message(confirm_message)

        pgp_address = PGPAddress.for_address(bart)
        self.assertEqual(pgp_address.key_fingerprint,
                         self.bart_new_key.fingerprint)
        self.assertTrue(pgp_address.key_confirmed)

    def test_change_extra_arg(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key change extra arguments', '')
        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('Extraneous argument/s: extra,arguments',
                      results_msg.get_payload())

    def test_change_no_email(self):
        message = _create_mixed('', 'test@example.com', 'key change')
        MIMEWrapper(message).attach_keys(self.bart_key.pubkey)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No email to change key of.', results_msg.get_payload())

    def test_change_no_pgp_address(self):
        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key change')
        MIMEWrapper(message).attach_keys(self.bart_key.pubkey)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('A pgp enabled address not found.',
                      results_msg.get_payload())

    def test_change_no_key_set(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key change')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn("You currently don't have a key set.",
                      results_msg.get_payload())

    def test_change_key_not_confirmed(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key change')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('Your key is currently not confirmed.',
                      results_msg.get_payload())

    def test_change_no_key(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        message = _create_plain('bart@example.com', 'test@example.com',
                                'key change', '')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No keys attached? Send a key.',
                      results_msg.get_payload())

    def test_change_multiple_keys(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        set_message = _create_mixed('bart@example.com', 'test@example.com',
                                    'key change')

        MIMEWrapper(set_message).attach_keys(self.bart_key.pubkey).attach_keys(
                self.bart_new_key.pubkey)

        items = _run_message(set_message, 1)
        results_msg = items[0].msg

        self.assertIn('More than one key! Send only one key.',
                      results_msg.get_payload())

    def test_change_private_key(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key change')
        MIMEWrapper(message).attach_keys(self.bart_key)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('You probably wanted to send your public key only.',
                      results_msg.get_payload())

    def test_change_no_encrypt_key(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key change')
        MIMEWrapper(message).attach_keys(self.unusable_key.pubkey)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn(
                'Need a key which can be used to encrypt communications.',
                results_msg.get_payload())

    def test_revoke_resets(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        revoc = self.bart_key.revoke(self.bart_key)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key revoke')
        MIMEWrapper(message).attach_revocs(revoc)

        items = _run_message(message, 2)
        if (items[0].msg['Subject'] ==
                'The results of your email commands'):  # pragma: no cover
            results_msg = items[0].msg
        else:
            results_msg = items[1].msg

        self.assertIsNone(pgp_address.key)
        self.assertFalse(pgp_address.key_confirmed)

        self.assertIn('Key needs to be reset.', results_msg.get_payload())

    def test_revoke_updates(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')

        test_key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 1024)
        uid = PGPUID.new('Some Name', email='anne@example.org')
        test_key.add_uid(uid,
                         usage={KeyFlags.Certify,
                                KeyFlags.EncryptCommunications,
                                KeyFlags.Sign},
                         hashes=[HashAlgorithm.SHA256,
                                 HashAlgorithm.SHA512],
                         ciphers=[SymmetricKeyAlgorithm.AES256],
                         compression=[CompressionAlgorithm.ZLIB])
        sub = PGPKey.new(PubKeyAlgorithm.ECDH, EllipticCurveOID.SECP256K1)
        test_key.add_subkey(sub, usage={KeyFlags.EncryptCommunications})

        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = test_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        revoc = test_key.revoke(sub.pubkey)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key revoke')
        MIMEWrapper(message).attach_revocs(revoc)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('Key succesfully updated.', results_msg.get_payload())
        sub = next(iter(pgp_address.key.subkeys.values()))
        revocs = list(sub.revocation_signatures)
        self.assertEqual(len(revocs), 1)
        self.assertEqual(revoc.hash2, revocs[0].hash2)

    def test_revoke_encrypted(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        revoc = self.bart_key.revoke(self.bart_key)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key revoke')
        MIMEWrapper(message).attach_revocs(revoc).encrypt(self.pgp_list.pubkey)

        items = _run_message(message, 2)
        if (items[0].msg['Subject'] ==
                'The results of your email commands'):  # pragma: no cover
            results_msg = items[0].msg
        else:
            results_msg = items[1].msg

        self.assertIsNone(pgp_address.key)
        self.assertFalse(pgp_address.key_confirmed)

        self.assertIn('Key needs to be reset.', results_msg.get_payload())

    def test_revoke_extra_arg(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key revoke extra arguments', '')
        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('Extraneous argument/s: extra,arguments',
                      results_msg.get_payload())

    def test_revoke_no_email(self):
        message = _create_mixed('', 'test@example.com', 'key revoke')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No email to revoke key of.', results_msg.get_payload())

    def test_revoke_no_pgp_address(self):
        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key revoke')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('A pgp enabled address not found.',
                      results_msg.get_payload())

    def test_revoke_no_key_set(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key revoke')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn("You currently don't have a key set.",
                      results_msg.get_payload())

    def test_revoke_key_not_confirmed(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key revoke')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('Your key is currently not confirmed.',
                      results_msg.get_payload())

    def test_revoke_no_revocs(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        message = _create_plain('bart@example.com', 'test@example.com',
                                'key revoke', '')
        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No key revocations attached? Send a key revocation.',
                      results_msg.get_payload())

    def test_sign(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        self.mlist.subscribe(bart)
        get_queue_messages('virgin')

        self.pgp_list.key_signing_allowed = {MemberRole.member}

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key sign')

        new_key = copy.copy(self.pgp_list.pubkey)
        uid = next(iter(new_key.userids))
        sig = self.bart_key.certify(uid)
        uid |= sig
        MIMEWrapper(message).attach_keys(new_key)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('List key updated with new signatures.',
                      results_msg.get_payload())

    def test_sign_encrypted(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        self.mlist.subscribe(bart)
        get_queue_messages('virgin')

        self.pgp_list.key_signing_allowed = {MemberRole.member}

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key sign')

        new_key = copy.copy(self.pgp_list.pubkey)
        uid = next(iter(new_key.userids))
        sig = self.bart_key.certify(uid)
        uid |= sig
        MIMEWrapper(message).attach_keys(new_key).encrypt(self.pgp_list.pubkey)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('List key updated with new signatures.',
                      results_msg.get_payload())

    def test_sign_extra_arg(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key sign extra arguments', '')
        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('Extraneous argument/s: extra,arguments',
                      results_msg.get_payload())

    def test_sign_no_email(self):
        message = _create_mixed('', 'test@example.com', 'key sign')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No email.', results_msg.get_payload())

    def test_sign_no_pgp_address(self):
        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key sign')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('A pgp enabled address not found.',
                      results_msg.get_payload())

    def test_sign_no_key_set(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key sign')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn("You currently don't have a key set.",
                      results_msg.get_payload())

    def test_sign_key_not_confirmed(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key sign')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('Your key is currently not confirmed.',
                      results_msg.get_payload())

    def test_sign_no_key(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        message = _create_plain('bart@example.com', 'test@example.com',
                                'key sign', '')

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No keys attached? Send a key.',
                      results_msg.get_payload())

    def test_sign_multiple_keys(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key sign')

        MIMEWrapper(message).attach_keys(self.bart_key.pubkey).attach_keys(
                self.bart_new_key.pubkey)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('More than one key! Send only one key.',
                      results_msg.get_payload())

    def test_sign_not_allowed(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        self.pgp_list.key_signing_allowed = {MemberRole.owner}

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key sign')
        MIMEWrapper(message).attach_keys(self.pgp_list.pubkey)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('You are not allowed to sign the list key.',
                      results_msg.get_payload())

    def test_sign_wrong_keymaterial(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        self.mlist.subscribe(bart)
        get_queue_messages('virgin')

        self.pgp_list.key_signing_allowed = {MemberRole.member}

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key sign')
        MIMEWrapper(message).attach_keys(self.bart_key.pubkey)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('You sent a wrong key.',
                      results_msg.get_payload())

    def test_sign_no_uids(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        self.mlist.subscribe(bart)
        get_queue_messages('virgin')

        self.pgp_list.key_signing_allowed = {MemberRole.member}

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key sign')
        new_key = copy.copy(self.pgp_list.pubkey)
        for uid in new_key.userids:
            new_key.del_uid(uid.email)

        MIMEWrapper(message).attach_keys(new_key)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No signed UIDs found.',
                      results_msg.get_payload())

    def test_sign_no_new_sig(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        self.mlist.subscribe(bart)
        get_queue_messages('virgin')

        self.pgp_list.key_signing_allowed = {MemberRole.member}

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key sign')
        MIMEWrapper(message).attach_keys(self.pgp_list.pubkey)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No new certifications found.',
                      results_msg.get_payload())

    def test_sign_no_sig_by_key(self):
        bart = getUtility(IUserManager).create_address('bart@example.com',
                                                       'Bart Person')
        with transaction() as t:
            pgp_address = PGPAddress(bart)
            pgp_address.key = self.bart_key.pubkey
            pgp_address.key_confirmed = True
            t.add(pgp_address)

        self.mlist.subscribe(bart)
        get_queue_messages('virgin')

        self.pgp_list.key_signing_allowed = {MemberRole.member}

        message = _create_mixed('bart@example.com', 'test@example.com',
                                'key sign')

        new_key = copy.copy(self.pgp_list.pubkey)
        uid = next(iter(new_key.userids))
        sig = self.bart_new_key.certify(uid)
        uid |= sig
        MIMEWrapper(message).attach_keys(new_key)

        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No new certifications found.',
                      results_msg.get_payload())


class TestGeneral(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        self.mlist = create_list('test@example.com', style_name='pgp-default')
        self.pgp_list = PGPMailingList.for_list(self.mlist)
        self.pgp_list.key = load_key('ecc_p256.priv.asc')

    def test_receive(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key receive', '')
        items = _run_message(message, 2)
        if (items[0].msg['Subject'] ==
                'The results of your email commands'):  # pragma: no cover
            pubkey_message = items[1].msg
        else:
            pubkey_message = items[0].msg

        wrapped = PGPWrapper(pubkey_message)
        self.assertTrue(wrapped.has_keys())
        keys = list(wrapped.keys())
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0].fingerprint, self.pgp_list.key.fingerprint)

    def test_receive_extra_arg(self):
        message = _create_plain('bart@example.com', 'test@example.com',
                                'key receive extra arguments', '')
        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('Extraneous argument/s: extra,arguments',
                      results_msg.get_payload())

    def test_receive_no_email(self):
        message = _create_plain('', 'test@example.com', 'key receive', '')
        items = _run_message(message, 1)
        results_msg = items[0].msg

        self.assertIn('No email to send list public key.',
                      results_msg.get_payload())
