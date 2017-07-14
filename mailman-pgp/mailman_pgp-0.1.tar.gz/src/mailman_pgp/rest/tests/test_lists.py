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
from unittest import TestCase
from urllib.error import HTTPError

from mailman.app.lifecycle import create_list
from mailman.testing.helpers import call_api
from pgpy import PGPKey

from mailman_pgp.database import mm_transaction
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.testing.layers import PGPRESTLayer


class TestLists(TestCase):
    layer = PGPRESTLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')

    def test_missing_list(self):
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'missing.example.com')
        self.assertEqual(cm.exception.code, 404)

    def test_all_lists(self):
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/')
        self.assertEqual(json['total_size'], 1)
        self.assertEqual(len(json['entries']), 1)
        lists = json['entries']
        plist = lists[0]
        self.assertEqual(plist['list_id'], self.mlist.list_id)

    def test_get_list(self):
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com')
        self.assertEqual(json['list_id'], self.mlist.list_id)
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test@example.com')
        self.assertEqual(json['list_id'], self.mlist.list_id)

    def test_get_list_key(self):
        with mm_transaction():
            mlist = create_list('another@example.com',
                                style_name='pgp-default')
            pgp_list = PGPMailingList.for_list(mlist)
            pgp_list.generate_key(True)

        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'another.example.com/pubkey')

        json.pop('http_etag')
        self.assertEqual(len(json.keys()), 2)
        self.assertIn('public_key', json.keys())
        self.assertIn('key_fingerprint', json.keys())

        key, _ = PGPKey.from_blob(json['public_key'])
        self.assertEqual(json['key_fingerprint'], key.fingerprint)
