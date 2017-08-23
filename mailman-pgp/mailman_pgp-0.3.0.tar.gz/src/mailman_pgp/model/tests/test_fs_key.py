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
import time
import unittest
from os.path import exists, join
from tempfile import TemporaryDirectory

from mailman_pgp.model.fs_key import FSKey
from mailman_pgp.testing.layers import PGPLayer
from mailman_pgp.testing.pgp import load_key


class TestFSKey(unittest.TestCase):
    layer = PGPLayer

    def setUp(self):
        self.tmpdir = TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_load(self):
        key_name = 'something.asc'
        key_path = join(self.tmpdir.name, key_name)
        key_data = load_key('rsa_1024.priv.asc')
        with open(key_path, 'w') as key_file:
            key_file.write(str(key_data))

        key = FSKey(self.tmpdir.name, key_name, False)
        self.assertEqual(key.key_path, key_path)

        key.load()
        self.assertEqual(key.key.fingerprint, key_data.fingerprint)

    def test_reload(self):
        key_name = 'something.asc'
        key_path = join(self.tmpdir.name, key_name)
        key_data = load_key('rsa_1024.priv.asc')
        new_key_data = load_key('ecc_p256.priv.asc')
        with open(key_path, 'w') as key_file:
            key_file.write(str(key_data))

        key = FSKey(self.tmpdir.name, key_name, True)

        time.sleep(2)
        with open(key_path, 'w') as key_file:
            key_file.write(str(new_key_data))

        key.reload()
        self.assertIsNotNone(key.key)
        self.assertEqual(key.key.fingerprint, new_key_data.fingerprint)

    def test_reload_none(self):
        key_name = 'something.asc'
        key = FSKey(self.tmpdir.name, key_name, False)
        key_data = load_key('rsa_1024.priv.asc')
        with open(key.key_path, 'w') as key_file:
            key_file.write(str(key_data))

        self.assertIsNone(key.key)
        key.reload()
        self.assertIsNotNone(key.key)
        self.assertEqual(key.key.fingerprint, key_data.fingerprint)

    def test_save(self):
        key_name = 'something.asc'
        key = FSKey(self.tmpdir.name, key_name)
        key_data = load_key('rsa_1024.priv.asc')

        key.key = key_data
        key.save()
        self.assertTrue(exists(key.key_path))

    def test_delete(self):
        key_name = 'something.asc'
        key_path = join(self.tmpdir.name, key_name)
        key_data = load_key('rsa_1024.priv.asc')
        with open(key_path, 'w') as key_file:
            key_file.write(str(key_data))

        key = FSKey(self.tmpdir.name, key_name, True)

        key.delete()
        self.assertFalse(exists(key.key_path))
        self.assertIsNotNone(key.key)

    def test_delete_none(self):
        key = FSKey(self.tmpdir.name, 'something.asc')
        key.delete()

    def test_shred(self):
        key_name = 'something.asc'
        key_path = join(self.tmpdir.name, key_name)
        key_data = load_key('rsa_1024.priv.asc')
        with open(key_path, 'w') as key_file:
            key_file.write(str(key_data))

        key = FSKey(self.tmpdir.name, key_name, True)

        key.shred()
        self.assertFalse(exists(key.key_path))
        self.assertIsNotNone(key.key)

    def test_shred_none(self):
        key = FSKey(self.tmpdir.name, 'something.asc')
        key.shred()
