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
from email import message_from_bytes
from unittest import TestCase

from mailman.email.message import Message
from pgpy import PGPKey
from pkg_resources import resource_string


def load_message(path):
    data = resource_string('mailman_pgp.pgp.tests',
                           os.path.join('data', 'messages', path))
    return message_from_bytes(data, Message)


def load_key(path):
    key, _ = PGPKey.from_blob(
            resource_string('mailman_pgp.pgp.tests',
                            os.path.join('data', 'keys', path)))
    return key


class WrapperTestCase(TestCase):
    wrapper = None

    def wrap(self, message):
        return self.wrapper(message)

    def is_signed(self, message, signed):
        wrapped = self.wrap(message)
        self.assertEqual(wrapped.is_signed(), signed)

    def sign(self, message, key):
        wrapped = self.wrap(message)
        signed = wrapped.sign(key)
        signed_wrapped = self.wrap(signed)
        self.assertTrue(signed_wrapped.is_signed())

    def sign_verify(self, message, priv, pub):
        wrapped = self.wrap(message)
        signed = wrapped.sign(priv)
        signed_wrapped = self.wrap(signed)
        for signature in signed_wrapped.verify(pub):
            self.assertTrue(bool(signature))

    def verify(self, message, key, valid):
        wrapped = self.wrap(message)
        for signature in wrapped.verify(key):
            self.assertEqual(bool(signature), valid)

    def is_encrypted(self, message, encrypted):
        wrapped = self.wrap(message)
        self.assertEqual(wrapped.is_encrypted(), encrypted)

    def encrypt(self, message, *keys, **kwargs):
        wrapped = self.wrap(message)
        encrypted = wrapped.encrypt(*keys, **kwargs)
        encrypted_wrapped = self.wrap(encrypted)
        self.assertTrue(encrypted_wrapped.is_encrypted())

    def encrypt_decrypt(self, message, pub, priv):
        wrapped = self.wrap(message)
        encrypted = wrapped.encrypt(pub)

        encrypted_wrapped = self.wrap(encrypted)
        decrypted = encrypted_wrapped.decrypt(priv)
        decrypted_wrapped = self.wrap(decrypted)

        self.assertFalse(decrypted_wrapped.is_encrypted())
        self.assertEqual(decrypted.get_payload(), message.get_payload())

    def decrypt(self, message, key, clear):
        wrapped = self.wrap(message)
        decrypted = wrapped.decrypt(key)
        decrypted_wrapped = self.wrap(decrypted)

        self.assertFalse(decrypted_wrapped.is_encrypted())
        self.assertEqual(decrypted.get_payload(), clear)

    def has_keys(self, message, has_keys):
        wrapped = self.wrap(message)
        self.assertEqual(wrapped.has_keys(), has_keys)

    def keys(self, message, keys):
        wrapped = self.wrap(message)
        loaded = list(wrapped.keys())
        self.assertEqual(len(loaded), len(keys))

        loaded_fingerprints = list(map(lambda key: key.fingerprint, loaded))
        fingerprints = list(map(lambda key: key.fingerprint, keys))
        self.assertListEqual(loaded_fingerprints, fingerprints)

    def sign_encrypt_decrypt_verify(self, message, sign_key, encrypt_key):
        wrapped = self.wrap(message)
        encrypted = wrapped.sign_encrypt(sign_key, encrypt_key.pubkey)
        encrypted_wrapped = self.wrap(encrypted)
        self.assertTrue(encrypted_wrapped.is_encrypted())

        decrypted = encrypted_wrapped.decrypt(encrypt_key)
        decrypted_wrapped = self.wrap(decrypted)
        self.assertTrue(decrypted_wrapped.is_signed())
        self.assertFalse(decrypted_wrapped.is_encrypted())

        verification = decrypted_wrapped.verify(sign_key.pubkey)
        for sig in verification:
            self.assertTrue(bool(sig))
        self.assertListEqual(list(decrypted_wrapped.get_signed()),
                             list(wrapped.get_payload()))

    def sign_then_encrypt_decrypt_verify(self, message, sign_key, encrypt_key):
        wrapped = self.wrap(message)
        encrypted = wrapped.sign_then_encrypt(sign_key, encrypt_key.pubkey)
        encrypted_wrapped = self.wrap(encrypted)
        self.assertTrue(encrypted_wrapped.is_encrypted())

        decrypted = encrypted_wrapped.decrypt(encrypt_key)
        decrypted_wrapped = self.wrap(decrypted)
        self.assertTrue(decrypted_wrapped.is_signed())
        self.assertFalse(decrypted_wrapped.is_encrypted())

        verification = decrypted_wrapped.verify(sign_key.pubkey)
        for sig in verification:
            self.assertTrue(bool(sig))
        self.assertListEqual(list(decrypted_wrapped.get_signed()),
                             list(wrapped.get_payload()))
