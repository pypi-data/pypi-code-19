# -*- coding: utf-8 -*-
# Copyright (C) 2017 Jan Jancar
#
# This file is a part of the Django Mailman PGP plugin.
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

from __future__ import absolute_import, unicode_literals

from itertools import chain

from mailmanclient import Address, MailingList
from mailmanclient.restbase.base import RESTObject
from pgpy import PGPKey
from pgpy.errors import PGPError


class PGPMailingList(RESTObject):
    _writable_properties = (
        'unsigned_msg_action', 'inline_pgp_action', 'expired_sig_action',
        'revoked_sig_action', 'invalid_sig_action', 'duplicate_sig_action',
        'strip_original_sig', 'sign_outgoing', 'nonencrypted_msg_action',
        'encrypt_outgoing', 'key_change_workflow', 'key_signing_allowed')
    _read_only_properties = ('self_link', 'list_id')
    _properties = tuple(chain(_writable_properties, _read_only_properties))

    @property
    def mlist(self):
        return MailingList(self._connection, 'lists/{}'.format(self.list_id))

    @property
    def key(self):
        try:
            response, content = self._connection.call(self._url + '/key')
            key, _ = PGPKey.from_blob(content['key'])
            return key
        except PGPError:
            return None

    @key.setter
    def key(self, value):
        str_key = str(value) if value else ''
        self._connection.call(self._url + '/key', data=dict(key=str_key),
                              method='PUT')

    @property
    def pubkey(self):
        try:
            response, content = self._connection.call(self._url + '/pubkey')
            key, _ = PGPKey.from_blob(content['public_key'])
            return key
        except PGPError:
            return None

    @pubkey.setter
    def pubkey(self, value):
        str_key = str(value) if value else ''
        self._connection.call(self._url + '/pubkey',
                              data=dict(public_key=str_key),
                              method='PUT')


class PGPAddress(RESTObject):
    _read_only_properties = ('self_link', 'email', 'key_fingerprint',
                             'key_confirmed')
    _properties = _read_only_properties

    @property
    def address(self):
        return Address(self._connection, 'addresses/{}'.format(self.email))
