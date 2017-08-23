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

import os
import unittest
from email import message_from_bytes
from operator import attrgetter

from mailman.email.message import Message
from pgpy import PGPKey
from pkg_resources import resource_string

from mailman_pgp.testing.layers import PGPLayer
from mailman_pgp.utils.pgp import revoc_from_blob


def load_blob(*path):
    return resource_string('mailman_pgp.pgp.tests',
                           os.path.join('data', *path))


def load_message(path):
    """
    :rtype: Message
    """
    return message_from_bytes(load_blob('messages', path), Message)


def load_key(path):
    """
    :rtype: pgpy.PGPKey
    """
    key, _ = PGPKey.from_blob(load_blob('keys', path))
    return key


def load_revoc(path):
    """
    :rtype: pgpy.PGPSignature
    """
    return revoc_from_blob(load_blob('revocs', path))


def payload_equal(one_msg, other_msg):
    one_payload = one_msg.get_payload()
    other_payload = other_msg.get_payload()
    if isinstance(one_payload, list) and isinstance(other_payload, list):
        if len(one_payload) != len(other_payload):
            return False
        for one_inner, other_inner in zip(one_payload, other_payload):
            if not payload_equal(one_inner, other_inner):
                return False
        return True
    else:
        return one_payload == other_payload


class WrapperTestCase(unittest.TestCase):
    layer = PGPLayer
    wrapper = None
    maxDiff = None

    def wrap(self, message):
        return self.wrapper(message)

    def is_signed(self, message, signed):
        wrapped = self.wrap(message)
        self.assertEqual(wrapped.is_signed(), signed)

    def has_signature(self, message, has):
        wrapped = self.wrap(message)
        self.assertEqual(wrapped.has_signature(), has)

    def sign(self, message, key):
        signed = self.wrap(message).sign(key)
        self.assertTrue(signed.is_signed())

    def sign_verify(self, message, priv, pub):
        signed = self.wrap(message).sign(priv)
        for signature in signed.verify(pub):
            self.assertTrue(bool(signature))

    def verify(self, message, key, valid):
        wrapped = self.wrap(message)
        for signature in wrapped.verify(key):
            self.assertEqual(bool(signature), valid)

    def is_encrypted(self, message, encrypted):
        wrapped = self.wrap(message)
        self.assertEqual(wrapped.is_encrypted(), encrypted)

    def has_encryption(self, message, has):
        wrapped = self.wrap(message)
        self.assertEqual(wrapped.has_encryption(), has)

    def encrypt(self, message, *keys, **kwargs):
        encrypted = self.wrap(message).encrypt(*keys, **kwargs)
        self.assertTrue(encrypted.is_encrypted())

    def encrypt_decrypt(self, message, pub, priv):
        decrypted = self.wrap(message).copy().encrypt(pub).decrypt(priv)

        self.assertFalse(decrypted.is_encrypted())
        self.assertTrue(payload_equal(decrypted.msg, message))

    def decrypt(self, message, key, clear):
        decrypted = self.wrap(message).copy().decrypt(key)

        self.assertFalse(decrypted.is_encrypted())
        self.assertEqual(decrypted.msg.get_payload(), clear)

    def has_keys(self, message, has_keys):
        wrapped = self.wrap(message)
        self.assertEqual(wrapped.has_keys(), has_keys)

    def is_keys(self, message, is_keys):
        wrapped = self.wrap(message)
        self.assertEqual(wrapped.is_keys(), is_keys)

    def keys(self, message, keys):
        wrapped = self.wrap(message)
        loaded = list(wrapped.keys())
        self.assertEqual(len(loaded), len(keys))

        loaded_fingerprints = list(map(attrgetter('fingerprint'), loaded))
        fingerprints = list(map(attrgetter('fingerprint'), keys))
        self.assertListEqual(loaded_fingerprints, fingerprints)

    def attach_keys(self, message, keys):
        wrapped = self.wrap(message).attach_keys(*keys)
        loaded = list(wrapped.keys())

        self.assertTrue(wrapped.has_keys())
        loaded_fingerprints = list(map(attrgetter('fingerprint'), loaded))
        fingerprints = list(map(attrgetter('fingerprint'), keys))
        self.assertListEqual(loaded_fingerprints, fingerprints)

    def has_revocs(self, message, has_revocs):
        wrapped = self.wrap(message)
        self.assertEqual(wrapped.has_revocs(), has_revocs)

    def is_revocs(self, message, is_revocs):
        wrapped = self.wrap(message)
        self.assertEqual(wrapped.is_revocs(), is_revocs)

    def revocs(self, message, revocs):
        wrapped = self.wrap(message)
        loaded = list(wrapped.revocs())
        self.assertEqual(len(loaded), len(revocs))

        loaded_issuers = list(map(attrgetter('signer'), loaded))
        issuers = list(map(attrgetter('signer'), revocs))
        self.assertListEqual(loaded_issuers, issuers)

    def attach_revocs(self, message, revocs):
        wrapped = self.wrap(message).attach_revocs(*revocs)
        loaded = list(wrapped.revocs())

        self.assertTrue(wrapped.has_revocs())
        loaded_issuers = list(map(attrgetter('signer'), loaded))
        issuers = list(map(attrgetter('signer'), revocs))
        self.assertListEqual(loaded_issuers, issuers)

    def sign_encrypt_decrypt_verify(self, message, sign_key, encrypt_key):
        wrapped = self.wrap(message)
        encrypted = wrapped.copy().sign_encrypt(sign_key, encrypt_key.pubkey)
        self.assertTrue(encrypted.is_encrypted())

        decrypted = encrypted.decrypt(encrypt_key)
        self.assertTrue(decrypted.is_signed())
        self.assertFalse(decrypted.is_encrypted())

        verification = decrypted.verify(sign_key.pubkey)
        for sig in verification:
            self.assertTrue(bool(sig))
        self.assertListEqual(list(decrypted.get_signed()),
                             list(wrapped.get_payload()))

    def sign_then_encrypt_decrypt_verify(self, message, sign_key, encrypt_key):
        wrapped = self.wrap(message)
        encrypted = wrapped.copy().sign(sign_key).encrypt(encrypt_key.pubkey)
        self.assertTrue(encrypted.is_encrypted())

        decrypted = encrypted.copy().decrypt(encrypt_key)
        self.assertTrue(decrypted.is_signed())
        self.assertFalse(decrypted.is_encrypted())

        verification = decrypted.verify(sign_key.pubkey)
        for sig in verification:
            self.assertTrue(bool(sig))
        self.assertListEqual(list(decrypted.get_signed()),
                             list(wrapped.get_payload()))

    def decrypt_verify(self, message, decrypt_key, verify_key, valid):
        wrapped = self.wrap(message)
        decrypted = wrapped.copy().decrypt(decrypt_key)

        self.assertFalse(decrypted.is_encrypted())
        self.assertTrue(decrypted.is_signed())

        verification = decrypted.verify(verify_key)
        for sig in verification:
            self.assertEqual(bool(sig), valid)
