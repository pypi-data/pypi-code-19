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
import unittest
from copy import copy
from urllib.error import HTTPError

from mailman.app.lifecycle import create_list
from mailman.interfaces.action import Action
from mailman.interfaces.member import MemberRole
from mailman.testing.helpers import call_api
from pgpy import PGPKey

from mailman_pgp.database import mm_transaction, transaction
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.testing.layers import PGPRESTLayer
from mailman_pgp.testing.pgp import load_key


class TestLists(unittest.TestCase):
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


class TestListConfig(unittest.TestCase):
    layer = PGPRESTLayer

    def setUp(self):
        with mm_transaction():
            self.mlist = create_list('test@example.com',
                                     style_name='pgp-default')

        self.list_key = load_key('ecc_p256.priv.asc')
        with transaction():
            self.pgp_list = PGPMailingList.for_list(self.mlist)
            self.pgp_list.key = self.list_key

    def test_get(self):
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com')
        cfg = dict(unsigned_msg_action='reject',
                   inline_pgp_action='defer',
                   expired_sig_action='reject',
                   revoked_sig_action='reject',
                   invalid_sig_action='reject',
                   duplicate_sig_action='reject',
                   strip_original_sig=False,
                   sign_outgoing=False,
                   nonencrypted_msg_action='reject',
                   encrypt_outgoing=True,
                   key_change_workflow='pgp-key-change-mod-workflow',
                   key_signing_allowed=['moderator', 'owner'])

        for key in cfg:
            value = json[key]
            if isinstance(value, list):
                value = sorted(value)
            self.assertEqual(cfg[key], value)

    def test_put(self):
        cfg = dict(unsigned_msg_action='defer',
                   inline_pgp_action='defer',
                   expired_sig_action='defer',
                   revoked_sig_action='defer',
                   invalid_sig_action='defer',
                   duplicate_sig_action='defer',
                   strip_original_sig=False,
                   sign_outgoing=True,
                   nonencrypted_msg_action='defer',
                   encrypt_outgoing=False,
                   key_change_workflow='pgp-key-change-mod-workflow',
                   key_signing_allowed=['member', 'owner'])
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com',
                data=cfg,
                method='PUT')

        self.assertEqual(response.status_code, 204)
        for key in cfg:
            attr = getattr(self.pgp_list, key)
            if isinstance(attr, Action):
                attr = attr.name
            elif key == 'key_signing_allowed':
                attr = sorted(enum.name for enum in attr)
            self.assertEqual(attr, cfg[key])

    def test_put_wrong_value(self):
        cfg = dict(unsigned_msg_action='not-an-action',
                   inline_pgp_action='defer',
                   expired_sig_action='defer',
                   revoked_sig_action='defer',
                   invalid_sig_action='defer',
                   duplicate_sig_action='defer',
                   strip_original_sig=False,
                   sign_outgoing=True,
                   nonencrypted_msg_action='defer',
                   encrypt_outgoing=False,
                   key_change_workflow='pgp-key-change-mod-workflow',
                   key_signing_allowed=['member', 'owner'])
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'test.example.com',
                     data=cfg,
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

    def test_patch_set(self):
        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com',
                data=dict(key_signing_allowed=['member', 'owner']),
                method='PATCH')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.pgp_list.key_signing_allowed,
                         {MemberRole.member, MemberRole.owner})

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


class TestListKey(unittest.TestCase):
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

    def test_set_list_key_public(self):
        new_key = load_key('rsa_1024.priv.asc')
        with self.assertRaises(HTTPError) as cm:
            call_api('http://localhost:9001/3.1/plugins/pgp/lists/'
                     'test.example.com/key',
                     data=dict(key=str(new_key.pubkey)),
                     method='PUT')

        self.assertEqual(cm.exception.code, 400)

        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com/key')

        key, _ = PGPKey.from_blob(json['key'])
        self.assertEqual(key.fingerprint, self.list_key.fingerprint)

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

    def test_set_list_pubkey(self):
        signer_key = load_key('rsa_1024.priv.asc')
        signed = copy(self.list_key.pubkey)
        uid = next(iter(signed.userids))
        sig = signer_key.certify(uid)
        uid |= sig

        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com/pubkey',
                data=dict(public_key=str(signed)),
                method='PUT')

        self.assertEqual(response.status_code, 202)

        json, response = call_api(
                'http://localhost:9001/3.1/plugins/pgp/lists/'
                'test.example.com/pubkey')

        key, _ = PGPKey.from_blob(json['public_key'])
        uid = next(iter(key.userids))
        self.assertIn(sig, list(uid.signatures))
