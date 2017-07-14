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

"""Signature checking rule for the pgp-posting-chain."""
import logging

from mailman.core.i18n import _
from mailman.interfaces.action import Action
from mailman.interfaces.rules import IRule
from mailman.interfaces.usermanager import IUserManager
from public import public
from zope.component import getUtility
from zope.interface import implementer

from mailman_pgp.database import query
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.wrapper import PGPWrapper

log = logging.getLogger('mailman.plugin.pgp')


def record_action(msg, msgdata, action, sender, reason):
    log.info('[pgp] {}{}: {}'.format(
            action.name, msg.get('message-id', 'n/a'), reason))
    msgdata['moderation_action'] = action.name
    msgdata['moderation_sender'] = sender
    msgdata.setdefault('moderation_reasons', []).append(reason)


@public
@implementer(IRule)
class Signature:
    """The signature checking rule."""

    name = 'signature'
    description = _(
            "A rule which enforces PGP enabled list signature configuration.")
    record = True

    def check(self, mlist, msg, msgdata):
        """See `IRule`."""
        # Find the `PGPMailingList` this is for.
        pgp_list = query(PGPMailingList).filter_by(
                list_id=mlist.list_id).first()
        if pgp_list is None:
            raise ValueError('PGP enabled mailing list not found.')

        # Wrap the message to work with it.
        wrapped = PGPWrapper(msg)

        # Take unsigned_msg_action if unsigned.
        if not wrapped.is_signed():
            action = pgp_list.unsigned_msg_action
            if action != Action.defer:
                record_action(msg, msgdata, action, msg.sender,
                              'The message is unsigned.')
                return True

        # Take `inline_pgp_action` if inline signed.
        if wrapped.inline.is_signed():
            action = pgp_list.inline_pgp_action
            if action != Action.defer:
                record_action(msg, msgdata, action, msg.sender,
                              'Inline PGP is not allowed.')
                return True

        # Lookup the address by sender, and its corresponding `PGPAddress`.
        user_manager = getUtility(IUserManager)
        sender = msg.sender
        address = user_manager.get_address(sender)
        pgp_address = PGPAddress.for_address(address)
        if pgp_address is None:
            raise ValueError('PGP enabled address not found.')

        # See if we have a key.
        key = pgp_address.key
        if key is None:
            raise ValueError('No key?')

        # Take the `invalid_sig_action` if the verification failed.
        if not wrapped.verifies(key):
            action = pgp_list.invalid_sig_action
            if action != Action.defer:
                record_action(msg, msgdata, action, msg.sender,
                              'Signature did not verify.')
                return True

        # XXX: we need to track key revocation separately to use it here
        # TODO: check key revocation here

        return False
