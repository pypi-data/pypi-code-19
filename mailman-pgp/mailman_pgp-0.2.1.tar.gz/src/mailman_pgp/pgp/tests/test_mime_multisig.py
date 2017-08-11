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

"""Tests for the MultiSig wrapper."""
from parameterized import parameterized

from mailman_pgp.pgp.mime_multisig import MIMEMultiSigWrapper
from mailman_pgp.testing.pgp import load_key, load_message, WrapperTestCase


class MultiSigWrapperTestCase(WrapperTestCase):
    wrapper = MIMEMultiSigWrapper


class TestSigning(MultiSigWrapperTestCase):
    @parameterized.expand([
        (load_message('mime_signed.eml'),
         False),
        (load_message('mime_signed_invalid.eml'),
         False),
        (load_message('mime_multisig.eml'),
         True),
        (load_message('mime_multisig_invalid.eml'),
         True),
        (load_message('clear.eml'),
         False),
        (load_message('clear_multipart.eml'),
         False)
    ])
    def test_is_signed(self, message, signed):
        self.is_signed(message, signed)

    @parameterized.expand([
        (load_message('mime_signed.eml'),
         False),
        (load_message('mime_signed_invalid.eml'),
         False),
        (load_message('mime_multisig.eml'),
         True),
        (load_message('mime_multisig_invalid.eml'),
         True),
        (load_message('clear.eml'),
         False),
        (load_message('clear_multipart.eml'),
         False)
    ])
    def test_has_signature(self, message, has):
        self.has_signature(message, has)

    @parameterized.expand([
        (load_message('clear.eml'),
         load_key('rsa_1024.priv.asc')),
        (load_message('clear_multipart.eml'),
         load_key('ecc_p256.priv.asc'))
    ])
    def test_sign(self, message, key):
        self.sign(message, key)

    @parameterized.expand([
        (load_message('clear.eml'),
         load_key('rsa_1024.priv.asc'),
         load_key('rsa_1024.pub.asc')),
        (load_message('clear_multipart.eml'),
         load_key('ecc_p256.priv.asc'),
         load_key('ecc_p256.pub.asc')),
        (load_message('mime_multisig.eml'),
         load_key('ecc_p256.priv.asc'),
         load_key('ecc_p256.pub.asc'))
    ])
    def test_sign_verify(self, message, priv, pub):
        self.sign_verify(message, priv, pub)

    @parameterized.expand([
        (load_message('mime_multisig.eml'),
         load_key('rsa_1024.pub.asc'),
         True),
        (load_message('mime_multisig_invalid.eml'),
         load_key('rsa_1024.pub.asc'),
         False)
    ])
    def test_verify(self, message, key, valid):
        self.verify(message, key, valid)


class TestCombined(MultiSigWrapperTestCase):
    @parameterized.expand([
        (load_message('clear.eml'),
         load_key('rsa_1024.priv.asc'),
         load_key('ecc_p256.priv.asc')),
        (load_message('clear_multipart.eml'),
         load_key('rsa_1024.priv.asc'),
         load_key('ecc_p256.priv.asc'))
    ])
    def test_sign_encrypt_decrypt_verify(self, message, sign_key, encrypt_key):
        self.sign_encrypt_decrypt_verify(message, sign_key, encrypt_key)

    @parameterized.expand([
        (load_message('clear.eml'),
         load_key('rsa_1024.priv.asc'),
         load_key('ecc_p256.priv.asc')),
        (load_message('clear_multipart.eml'),
         load_key('rsa_1024.priv.asc'),
         load_key('ecc_p256.priv.asc'))
    ])
    def test_sign_then_encrypt_decrypt_verify(self, message, sign_key,
                                              encrypt_key):
        self.sign_then_encrypt_decrypt_verify(message, sign_key, encrypt_key)

    @parameterized.expand([
        (load_message('mime_encrypted_signed.eml'),
         load_key('rsa_1024.priv.asc'),
         load_key('rsa_1024.pub.asc'),
         True)
    ])
    def test_decrypt_verify(self, message, decrypt_key, verify_key, valid):
        self.decrypt_verify(message, decrypt_key, verify_key, valid)
