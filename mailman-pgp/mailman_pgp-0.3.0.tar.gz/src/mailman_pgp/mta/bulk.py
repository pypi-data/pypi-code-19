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

"""PGP enabled BulkDelivery."""
import copy

from mailman.mta.bulk import BulkDelivery
from public import public

from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.mime import MIMEWrapper


class CallbackBulkDelivery(BulkDelivery):
    """Bulk delivery that has a list of callbacks to run for each chunk."""

    def __init__(self, max_recipients=None):
        super().__init__(max_recipients=max_recipients)
        self.callbacks = []

    def deliver(self, mlist, msg, msgdata):
        """See `IMailTransportAgentDelivery`."""
        refused = {}
        for recipients in self.chunkify(msgdata.get('recipients', set())):
            message_copy = copy.deepcopy(msg)
            msgdata_copy = msgdata.copy()
            recipients_copy = set(recipients)

            for callback in self.callbacks:
                callback(mlist, message_copy, msgdata_copy, recipients_copy)
            callback_refused = dict(
                    (recipient, (444, BaseException))
                    for recipient in recipients - recipients_copy)
            refused.update(callback_refused)

            chunk_refused = self._deliver_to_recipients(
                    mlist, message_copy, msgdata_copy, recipients_copy)
            refused.update(chunk_refused)
        return refused


class PGPBulkMixin:
    """Bulk encryption and signing Delivery mixin."""

    def sign_encrypt(self, mlist, msg, msgdata, recipients):
        """
        Sign and encrypt the outgoing message to the recipients.

        :param mlist:
        :type mlist: mailman.model.mailinglist.MailingList
        :param msg:
        :type msg: mailman.email.message.Message
        :param msgdata:
        :type msgdata: dict
        :param recipients:
        :type recipients: set
        """
        pgp_list = PGPMailingList.for_list(mlist)
        if not pgp_list:
            return
        if not pgp_list.encrypt_outgoing and not pgp_list.sign_outgoing:
            # nothing to do
            return

        keys = []
        for recipient in set(recipients):
            pgp_address = PGPAddress.for_email(recipient)
            if pgp_address is None:
                recipients.remove(recipient)
                continue
            if pgp_address.key is None or not pgp_address.key_confirmed:
                recipients.remove(recipient)
                continue
            keys.append(pgp_address.key)

        wrapped = MIMEWrapper(msg)
        if pgp_list.sign_outgoing:
            if pgp_list.encrypt_outgoing:
                wrapped.sign_encrypt(pgp_list.key, pgp_list.pubkey,
                                     *keys, throw_keyid=True)
            else:
                wrapped.sign(pgp_list.key)
        else:
            # Definitely encrypt here, the case where we don't encrypt or sign
            # is handled above at the start of the func.
            wrapped.encrypt(pgp_list.pubkey, *keys, throw_keyid=True)


@public
class PGPBulkDelivery(CallbackBulkDelivery, PGPBulkMixin):
    """Bulk PGP enabled delivery."""

    def __init__(self, max_recipients=None):
        super().__init__(max_recipients=max_recipients)
        self.callbacks.append(self.sign_encrypt)
