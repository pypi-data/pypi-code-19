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

from os.path import exists, isfile, join
from tempfile import TemporaryDirectory
from unittest import TestCase

from pgpy import PGPKey
from pgpy.constants import PubKeyAlgorithm
from public import public

from mailman_pgp.pgp.keygen import ListKeyGenerator


@public
class TesKeygen(TestCase):
    def setUp(self):
        self.keypair_config = {
            'key_type': PubKeyAlgorithm.RSAEncryptOrSign,
            'key_length': 1024,
            'subkey_type': PubKeyAlgorithm.RSAEncryptOrSign,
            'subkey_length': 1024
        }
        self.display_name = 'Display Name'
        self.posting_address = 'posting@address.com'
        self.request_address = 'posting-request@address.com'

    def test_generate(self):
        with TemporaryDirectory() as temp_dir:
            key_path = join(temp_dir, 'key.asc')
            keygen = ListKeyGenerator(self.keypair_config, self.display_name,
                                      self.posting_address,
                                      self.request_address, key_path)
            keygen.start()
            keygen.join()
            self.assertTrue(exists(key_path))
            self.assertTrue(isfile(key_path))

            key, _ = PGPKey.from_file(key_path)
            self.assertEqual(key.key_algorithm,
                             self.keypair_config['key_type'])
            self.assertEqual(key.key_size,
                             self.keypair_config['key_length'])

            subs = key.subkeys
            self.assertEqual(len(subs), 1)

            keyid, sub = subs.popitem()
            self.assertEqual(sub.key_algorithm,
                             self.keypair_config['subkey_type'])
            self.assertEqual(sub.key_size,
                             self.keypair_config['subkey_length'])

            uids = key.userids
            self.assertEqual(len(uids), 2)
            for uid in uids:
                self.assertEqual(uid.name, self.display_name)
                self.assertIn(uid.email,
                              (self.posting_address, self.request_address))
