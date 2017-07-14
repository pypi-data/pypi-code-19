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
from mailman.email.message import UserNotification
from mailman.interfaces.subscriptions import TokenOwner
from pgpy import PGPKey

from mailman_pgp.database import transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.utils import copy_headers
from mailman_pgp.pgp.wrapper import PGPWrapper

KEY_REQUEST = """\
----------
TODO: this is a pgp enabled list.
We need your pubkey.
Reply to this message with it as a PGP/MIME(preferred) or inline.
----------"""

CONFIRM_REQUEST = """\
----------
TODO: this is a pgp enabled list.
Reply to this message with this whole text
signed with your supplied key, either inline or PGP/MIME.

Fingerprint: {}
Token: {}
----------
"""


class PGPMixin:
    def _step_pgp_prepare(self):
        pgp_address = PGPAddress.for_address(self.address)
        if pgp_address is None:
            with transaction() as t:
                pgp_address = PGPAddress(self.address)
                t.add(pgp_address)


class SetPubkeyMixin:
    def __init__(self, pubkey=None):
        self.pubkey = pubkey

    @property
    def pubkey_key(self):
        if self.pubkey is None:
            return None
        return str(self.pubkey)

    @pubkey_key.setter
    def pubkey_key(self, value):
        if value is not None:
            self.pubkey, _ = PGPKey.from_blob(value)
        else:
            self.pubkey = None

    def _step_pubkey_checks(self):
        pgp_address = PGPAddress.for_address(self.address)
        assert pgp_address is not None

        if self.pubkey is None:
            if pgp_address.key is None:
                self.push('send_key_request')
        else:
            with transaction():
                pgp_address.key = self.pubkey

    def _step_send_key_request(self):
        self._set_token(TokenOwner.subscriber)
        self.push('receive_key')
        self.save()
        request_address = self.mlist.request_address
        email_address = self.address.email
        msg = UserNotification(email_address, request_address,
                               'key set {}'.format(self.token),
                               KEY_REQUEST)
        msg.send(self.mlist, add_precedence=False)
        # Now we wait for the confirmation.
        raise StopIteration

    def _step_receive_key(self):
        self._restore_subscriber()
        self._set_token(TokenOwner.no_one)


class ConfirmPubkeyMixin:
    def __init__(self, pre_confirmed=False):
        self.pubkey_confirmed = pre_confirmed

    def _step_pubkey_confirmation(self):
        pgp_address = PGPAddress.for_address(self.address)
        assert pgp_address is not None

        if self.pubkey_confirmed:
            with transaction():
                pgp_address.key_confirmed = True
        else:
            if not pgp_address.key_confirmed:
                self.push('send_key_confirm_request')

    def _step_send_key_confirm_request(self):
        self._set_token(TokenOwner.subscriber)
        self.push('receive_key_confirmation')
        self.save()

        pgp_address = PGPAddress.for_address(self.address)
        request_address = self.mlist.request_address
        email_address = self.address.email
        msg = UserNotification(email_address, request_address,
                               'key confirm {}'.format(self.token),
                               CONFIRM_REQUEST.format(
                                       pgp_address.key_fingerprint,
                                       self.token))
        pgp_list = PGPMailingList.for_list(self.mlist)
        wrapped = PGPWrapper(msg)
        encrypted = wrapped.sign_encrypt(pgp_list.key, pgp_address.key)

        msg.set_payload(encrypted.get_payload())
        copy_headers(encrypted, msg, True)
        msg.send(self.mlist)
        raise StopIteration

    def _step_receive_key_confirmation(self):
        self._restore_subscriber()
        self._set_token(TokenOwner.no_one)
        with transaction():
            pgp_address = PGPAddress.for_address(self.address)
            pgp_address.key_confirmed = True
