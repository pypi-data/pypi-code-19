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

"""Tests for the inline wrapper."""

from parameterized import parameterized
from public import public

from mailman_pgp.pgp.inline import InlineWrapper
from mailman_pgp.pgp.tests.base import load_key, load_message, WrapperTestCase


class InlineWrapperTestCase(WrapperTestCase):
    wrapper = InlineWrapper


@public
class TestSigning(InlineWrapperTestCase):
    @parameterized.expand([
        (load_message('inline_cleartext_signed.eml'),
         True),
        (load_message('inline_cleartext_signed_invalid.eml'),
         True),
        (load_message('inline_signed.eml'),
         True),
        (load_message('inline_signed_corrupted.eml'),
         False),
        (load_message('clear.eml'),
         False),
        (load_message('inline_encrypted.eml'),
         False)
    ])
    def test_is_signed(self, message, signed):
        self.is_signed(message, signed)

    @parameterized.expand([
        (load_message('clear.eml'),
         load_key('rsa_1024.priv.asc')),
        (load_message('clear.eml'),
         load_key('ecc_p256.priv.asc'))
    ])
    def test_sign(self, message, key):
        self.sign(message, key)

    @parameterized.expand([
        (load_message('clear.eml'),
         load_key('rsa_1024.priv.asc'),
         load_key('rsa_1024.pub.asc')),
        (load_message('clear.eml'),
         load_key('ecc_p256.priv.asc'),
         load_key('ecc_p256.pub.asc'))
    ])
    def test_sign_verify(self, message, priv, pub):
        self.sign_verify(message, priv, pub)

    @parameterized.expand([
        (load_message('inline_cleartext_signed.eml'),
         load_key('rsa_1024.pub.asc'),
         True),
        (load_message('inline_cleartext_signed_invalid.eml'),
         load_key('rsa_1024.pub.asc'),
         False),
        (load_message('inline_signed.eml'),
         load_key('rsa_1024.pub.asc'),
         True),
        (load_message('inline_signed_corrupted.eml'),
         load_key('rsa_1024.pub.asc'),
         False),
    ])
    def test_verify(self, message, key, valid):
        self.verify(message, key, valid)


@public
class TestEncryption(InlineWrapperTestCase):
    @parameterized.expand([
        (load_message('inline_encrypted.eml'),
         True),
        (load_message('inline_cleartext_signed.eml'),
         False),
        (load_message('inline_cleartext_signed_invalid.eml'),
         False),
        (load_message('inline_signed.eml'),
         False),
        (load_message('inline_signed_corrupted.eml'),
         False),
        (load_message('clear.eml'),
         False)
    ])
    def test_is_encrypted(self, message, encrypted):
        self.is_encrypted(message, encrypted)

    @parameterized.expand([
        (load_message('clear.eml'),
         load_key('rsa_1024.pub.asc')),
        (load_message('clear.eml'),
         (load_key('rsa_1024.pub.asc'),
          load_key('ecc_p256.pub.asc')))
    ])
    def test_encrypt(self, message, keys, **kwargs):
        if isinstance(keys, tuple):
            self.encrypt(message, *keys, **kwargs)
        else:
            self.encrypt(message, keys, **kwargs)

    @parameterized.expand([
        (load_message('clear.eml'),
         load_key('rsa_1024.pub.asc'),
         load_key('rsa_1024.priv.asc')),
        (load_message('clear.eml'),
         load_key('ecc_p256.pub.asc'),
         load_key('ecc_p256.priv.asc'))
    ])
    def test_encrypt_decrypt(self, message, pub, priv):
        self.encrypt_decrypt(message, pub, priv)

    @parameterized.expand([
        (load_message('inline_encrypted.eml'),
         load_key('rsa_1024.priv.asc'),
         'Some encrypted text.\n\n')
    ])
    def test_decrypt(self, message, key, clear):
        self.decrypt(message, key, clear)


@public
class TestKeys(InlineWrapperTestCase):
    @parameterized.expand([
        (load_message('inline_privkey.eml'),
         True),
        (load_message('inline_pubkey.eml'),
         True),
        (load_message('clear.eml'),
         False),
        (load_message('inline_cleartext_signed.eml'),
         False)
    ])
    def test_has_keys(self, message, has_keys):
        self.has_keys(message, has_keys)

    @parameterized.expand([
        (load_message('inline_privkey.eml'),
         [load_key('rsa_1024.priv.asc')]),
        (load_message('inline_pubkey.eml'),
         [load_key('rsa_1024.pub.asc')])
    ])
    def test_keys(self, message, keys):
        self.keys(message, keys)


@public
class TestCombined(InlineWrapperTestCase):
    @parameterized.expand([
        (load_message('clear.eml'),
         load_key('rsa_1024.priv.asc'),
         load_key('ecc_p256.priv.asc'))
    ])
    def test_sign_encrypt_decrypt_verify(self, message, sign_key, encrypt_key):
        self.sign_encrypt_decrypt_verify(message, sign_key, encrypt_key)

    @parameterized.expand([
        (load_message('clear.eml'),
         load_key('rsa_1024.priv.asc'),
         load_key('ecc_p256.priv.asc'))
    ])
    def test_sign_then_encrypt_decrypt_verify(self, message, sign_key,
                                              encrypt_key):
        self.sign_then_encrypt_decrypt_verify(message, sign_key, encrypt_key)
