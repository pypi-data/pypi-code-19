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
from public import public

from mailman_pgp.database import transaction
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.wrapper import PGPWrapper

CONFIRM_REQUEST = """\
----------
TODO: this is a pgp enabled list.
Reply to this message with this whole text
signed with your supplied key, either inline or PGP/MIME.

Fingerprint: {}
Token: {}
----------
"""


@public
class ConfirmPubkeyMixin:
    def __init__(self, pre_confirmed=False):
        self.pubkey_confirmed = pre_confirmed

    def _step_pubkey_confirmation(self):
        assert self.pgp_address is not None

        if self.pubkey_confirmed:
            with transaction():
                self.pgp_address.key_confirmed = True
        else:
            if not self.pgp_address.key_confirmed:
                self.push('send_key_confirm_request')

    def _step_send_key_confirm_request(self):
        self._set_token(TokenOwner.subscriber)
        self.push('receive_key_confirmation')
        self.save()

        request_address = self.mlist.request_address
        email_address = self.address.email
        msg = UserNotification(email_address, request_address,
                               'key confirm {}'.format(self.token),
                               CONFIRM_REQUEST.format(
                                       self.pgp_address.key_fingerprint,
                                       self.token))
        pgp_list = PGPMailingList.for_list(self.mlist)
        PGPWrapper(msg).sign_encrypt(pgp_list.key, self.pgp_address.key)

        msg.send(self.mlist)
        raise StopIteration

    def _step_receive_key_confirmation(self):
        self._set_token(TokenOwner.no_one)
