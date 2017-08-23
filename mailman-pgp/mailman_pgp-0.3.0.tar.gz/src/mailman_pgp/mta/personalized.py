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

"""PGP enabled IndividualDelivery."""
from mailman.mta.base import IndividualDelivery
from mailman.mta.decorating import DecoratingMixin
from mailman.mta.personalized import PersonalizedMixin
from mailman.mta.verp import VERPMixin
from public import public

from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.mime import MIMEWrapper


class PGPIndividualMixin:
    """Individual encryption and signing Delivery mixin."""

    def sign_encrypt(self, mlist, msg, msgdata):
        """
        Sign and encrypt the outgoing message to the recipient.

        :param mlist:
        :type mlist: mailman.model.mailinglist.MailingList
        :param msg:
        :type msg: mailman.email.message.Message
        :param msgdata:
        :type msgdata: dict
        """
        pgp_list = PGPMailingList.for_list(mlist)
        if not pgp_list:
            return
        if not pgp_list.encrypt_outgoing and not pgp_list.sign_outgoing:
            # nothing to do
            return

        recipient = msgdata['recipient']
        pgp_address = PGPAddress.for_email(recipient)
        if pgp_address is None:
            msgdata['no_deliver'] = True
            return
        if pgp_address.key is None or not pgp_address.key_confirmed:
            msgdata['no_deliver'] = True
            return

        key = pgp_address.key
        wrapped = MIMEWrapper(msg)

        if pgp_list.sign_outgoing:
            if pgp_list.encrypt_outgoing:
                wrapped.sign_encrypt(pgp_list.key, key, pgp_list.pubkey)
            else:
                wrapped.sign(pgp_list.key)
        else:
            # Definitely encrypt here, the case where we don't encrypt or sign
            # is handled above at the start of the func.
            wrapped.encrypt(key, pgp_list.pubkey)


@public
class PGPPersonalizedDelivery(IndividualDelivery, VERPMixin, DecoratingMixin,
                              PersonalizedMixin, PGPIndividualMixin):
    """Individual PGP enabled delivery."""

    def __init__(self):
        super().__init__()
        self.callbacks.extend([
            self.avoid_duplicates,
            self.decorate,
            self.personalize_to,
            self.sign_encrypt
        ])

    def _deliver_to_recipients(self, mlist, msg, msgdata, recipients):
        if msgdata.get('no_deliver', False):
            return dict((recipient, (444, BaseException)) for recipient in
                        recipients)
        return super()._deliver_to_recipients(mlist, msg, msgdata, recipients)
