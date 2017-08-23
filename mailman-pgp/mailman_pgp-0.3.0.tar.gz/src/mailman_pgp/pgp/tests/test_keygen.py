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

"""Test the out-of-process key generator."""
import unittest
from os.path import exists, isfile

from mailman.app.lifecycle import create_list
from parameterized import parameterized
from pgpy.constants import EllipticCurveOID, PubKeyAlgorithm

from mailman_pgp.config import config
from mailman_pgp.database import mm_transaction
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.keygen import ListKeyGenerator
from mailman_pgp.testing.layers import PGPConfigLayer
from mailman_pgp.utils.pgp import key_from_file


class TestKeygen(unittest.TestCase):
    layer = PGPConfigLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')
        self.pgp_list = PGPMailingList.for_list(self.mlist)

    @parameterized.expand([
        # RSA + RSA
        (PubKeyAlgorithm.RSAEncryptOrSign, 1024,
         PubKeyAlgorithm.RSAEncryptOrSign, 1024),
        # ECDSA + ECDH
        (PubKeyAlgorithm.ECDSA, EllipticCurveOID.SECP256K1,
         PubKeyAlgorithm.ECDH, EllipticCurveOID.SECP256K1),
        # DSA + ECDH
        (PubKeyAlgorithm.DSA, 1024,
         PubKeyAlgorithm.ECDH, EllipticCurveOID.SECP256K1)
    ])
    def test_generate(self, primary_key_type, primary_key_size, sub_key_type,
                      sub_key_size):
        def reset_primary(primary_key_args):
            config.pgp.primary_key_args = primary_key_args

        self.addCleanup(reset_primary, config.pgp.primary_key_args)

        def reset_sub(sub_key_args):
            config.pgp.sub_key_args = sub_key_args

        self.addCleanup(reset_sub, config.pgp.sub_key_args)

        config.pgp.primary_key_args = (primary_key_type, primary_key_size)
        config.pgp.sub_key_args = (sub_key_type, sub_key_size)

        key_path = self.pgp_list.key_path
        keygen = ListKeyGenerator(self.pgp_list)
        ret_key = keygen.generate(True)
        list_key = self.pgp_list.key
        self.assertTrue(exists(key_path))
        self.assertTrue(isfile(key_path))

        key = key_from_file(key_path)
        self.assertEqual(key.key_algorithm, primary_key_type)
        self.assertEqual(key.key_size, primary_key_size)
        self.assertEqual(ret_key.fingerprint, key.fingerprint)
        self.assertEqual(list_key.fingerprint, key.fingerprint)

        subs = key.subkeys
        self.assertEqual(len(subs), 1)

        keyid, sub = subs.popitem()
        self.assertEqual(sub.key_algorithm, sub_key_type)
        self.assertEqual(sub.key_size, sub_key_size)

        uids = key.userids
        self.assertEqual(len(uids), 2)
        for uid in uids:
            self.assertEqual(uid.name, self.pgp_list.mlist.display_name)
            self.assertIn(uid.email,
                          (self.pgp_list.mlist.posting_address,
                           self.pgp_list.mlist.request_address))
