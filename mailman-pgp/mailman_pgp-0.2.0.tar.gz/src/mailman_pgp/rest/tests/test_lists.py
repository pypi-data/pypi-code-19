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
from unittest import TestCase
from urllib.error import HTTPError

from mailman.app.lifecycle import create_list
from mailman.interfaces.action import Action
from mailman.testing.helpers import call_api
from pgpy import PGPKey

from mailman_pgp.database import mm_transaction, transaction
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.testing.layers import PGPRESTLayer
from mailman_pgp.testing.pgp import load_key


class TestLists(TestCase):
    layer = PGPRESTLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')

        self.list_key = load_key('ecc_p256.priv.asc')
        with transaction():
            self.pgp_list = PGPMailingList.for_list(self.mlist)
            self.pgp_list.key = self.list_key

    def test_missing_list(self):
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'missing.example.com')
        self.assertEqual(cm.exception.code, 404)
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'missing.example.com/key')
        self.assertEqual(cm.exception.code, 404)
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'missing.example.com/pubkey')
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


class TestListConfig(TestCase):
    layer = PGPRESTLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')

        self.list_key = load_key('ecc_p256.priv.asc')
        with transaction():
            self.pgp_list = PGPMailingList.for_list(self.mlist)
            self.pgp_list.key = self.list_key

    def test_put(self):
        config = dict(unsigned_msg_action='defer',
                      inline_pgp_action='defer',
                      expired_sig_action='defer',
                      revoked_sig_action='defer',
                      invalid_sig_action='defer',
                      duplicate_sig_action='defer',
                      strip_original_sig=False,
                      sign_outgoing=True,
                      nonencrypted_msg_action='defer',
                      encrypt_outgoing=False)
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com',
                data=config,
                method='PUT')

        self.assertEqual(response.status_code, 204)
        for key in config:
            attr = getattr(self.pgp_list, key)
            if isinstance(attr, Action):
                attr = attr.name
            self.assertEqual(attr, config[key])

    def test_put_wrong_value(self):
        config = dict(unsigned_msg_action='not-an-action',
                      inline_pgp_action='defer',
                      expired_sig_action='defer',
                      revoked_sig_action='defer',
                      invalid_sig_action='defer',
                      duplicate_sig_action='defer',
                      strip_original_sig=False,
                      sign_outgoing=True,
                      nonencrypted_msg_action='defer',
                      encrypt_outgoing=False)
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'test.example.com',
                     data=config,
                     method='PUT')
        self.assertEqual(cm.exception.code, 400)

    def test_patch(self):
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com',
                data=dict(unsigned_msg_action='defer'),
                method='PATCH')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.pgp_list.unsigned_msg_action, Action.defer)

    def test_patch_wrong_attribute(self):
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'test.example.com',
                     data=dict(something_something='somewhere'),
                     method='PATCH')
        self.assertEqual(cm.exception.code, 400)

    def test_patch_wrong_value(self):
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'test.example.com',
                     data=dict(unsigned_msg_action='not-an-action'),
                     method='PATCH')
        self.assertEqual(cm.exception.code, 400)

    def test_missing_list(self):
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'missing.example.com',
                     data=dict(),
                     method='PUT')
        self.assertEqual(cm.exception.code, 404)
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'missing.example.com',
                     data=dict(),
                     method='PATCH')
        self.assertEqual(cm.exception.code, 404)


class TestListKey(TestCase):
    layer = PGPRESTLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')

        self.list_key = load_key('ecc_p256.priv.asc')
        with transaction():
            self.pgp_list = PGPMailingList.for_list(self.mlist)
            self.pgp_list.key = self.list_key

    def test_get_list_key(self):
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com/key')
        json.pop('http_etag')
        self.assertEqual(len(json.keys()), 2)
        self.assertIn('key', json.keys())
        self.assertIn('key_fingerprint', json.keys())

        key, _ = PGPKey.from_blob(json['key'])
        self.assertFalse(key.is_public)
        self.assertEqual(json['key_fingerprint'], key.fingerprint)
        self.assertEqual(self.list_key.fingerprint, key.fingerprint)

    def test_missing_list_key(self):
        with transaction():
            self.pgp_list.key = None
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'test.example.com/key')
        self.assertEqual(cm.exception.code, 404)

    def test_set_list_key(self):
        new_key = load_key('rsa_1024.priv.asc')
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com/key',
                data=dict(key=str(new_key)),
                method='PUT')

        self.assertEqual(response.status_code, 202)

        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com/key')

        key, _ = PGPKey.from_blob(json['key'])
        self.assertEqual(key.fingerprint, new_key.fingerprint)

    def test_set_list_key_wrong(self):
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'test.example.com/key',
                     dict(key='some stuff?'),
                     method='PUT')
        self.assertEqual(cm.exception.code, 400)

    def test_get_list_pubkey(self):
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com/pubkey')

        json.pop('http_etag')
        self.assertEqual(len(json.keys()), 2)
        self.assertIn('public_key', json.keys())
        self.assertIn('key_fingerprint', json.keys())

        key, _ = PGPKey.from_blob(json['public_key'])
        self.assertTrue(key.is_public)
        self.assertEqual(json['key_fingerprint'], key.fingerprint)
        self.assertEqual(self.list_key.fingerprint, key.fingerprint)

    def test_missing_list_pubkey(self):
        with transaction():
            self.pgp_list.key = None
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'test.example.com/pubkey')
        self.assertEqual(cm.exception.code, 404)
