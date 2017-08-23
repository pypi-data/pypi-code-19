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
import datetime
import time
import unittest

from parameterized import parameterized
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm, EllipticCurveOID, HashAlgorithm, KeyFlags,
    PubKeyAlgorithm, SymmetricKeyAlgorithm)

from mailman_pgp.testing.layers import PGPLayer
from mailman_pgp.testing.pgp import load_blob, load_key
from mailman_pgp.utils.pgp import key_usable, revoc_from_blob


class TestPGPUtils(unittest.TestCase):
    layer = PGPLayer

    @parameterized.expand([
        (load_blob('revocs', 'rsa_1024.revoc.asc'),
         load_key('rsa_1024.pub.asc')),
        (load_blob('revocs', 'ecc_secp256k1.revoc.asc'),
         load_key('ecc_secp256k1.pub.asc')),
        (load_blob('revocs', 'ecc_p256.revoc.asc'),
         load_key('ecc_p256.pub.asc'))
    ])
    def test_revoc_from_blob_valid(self, blob, key):
        revoc = revoc_from_blob(blob)
        verifies = key.verify(key, revoc)
        self.assertTrue(bool(verifies))

    @parameterized.expand([
        ('Not an ASCII-Armored blob',),
        (load_blob('keys', 'rsa_1024.pub.asc'),),
    ])
    def test_revoc_from_blob_invalid(self, blob):
        self.assertRaises(ValueError, revoc_from_blob, blob)

    def test_key_usable(self):
        key = load_key('rsa_1024.priv.asc')

        self.assertTrue(key_usable(key.pubkey,
                                   {KeyFlags.Certify, KeyFlags.Sign,
                                    KeyFlags.EncryptCommunications,
                                    KeyFlags.EncryptStorage}))

    def test_key_usable_expired(self):
        key = PGPKey.new(PubKeyAlgorithm.ECDSA, EllipticCurveOID.SECP256K1)
        uid = PGPUID.new('Some Name', email='anne@example.org')
        key.add_uid(uid, key_expiration=datetime.timedelta(seconds=1),
                    usage={KeyFlags.Certify,
                           KeyFlags.Authentication,
                           KeyFlags.Sign},
                    hashes=[HashAlgorithm.SHA256,
                            HashAlgorithm.SHA512],
                    ciphers=[SymmetricKeyAlgorithm.AES256],
                    compression=[CompressionAlgorithm.ZLIB])

        time.sleep(2)

        self.assertFalse(key_usable(key.pubkey, set()))

    def test_key_usable_revoked_uid(self):
        key = load_key('ecc_p256.priv.asc')
        uid = next(iter(key.userids))
        rsig = key.revoke(uid)
        uid |= rsig
        self.assertFalse(key_usable(key.pubkey, {KeyFlags.Sign}))

    def test_key_usable_revoked(self):
        key = load_key('ecc_p256.priv.asc')
        rsig = key.revoke(key)
        key |= rsig

        self.assertFalse(key_usable(key.pubkey, set()))

    def test_key_usable_subkey_revoked(self):
        key = load_key('ecc_p256.priv.asc')
        sub = next(iter(key.subkeys.values()))
        rsig = key.revoke(sub)
        sub |= rsig

        self.assertFalse(
                key_usable(key.pubkey, {KeyFlags.EncryptCommunications}))
