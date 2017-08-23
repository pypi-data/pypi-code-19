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
from operator import attrgetter

from mailman.core.i18n import _
from mailman.interfaces.action import Action
from mailman.interfaces.chain import AcceptEvent
from mailman.interfaces.rules import IRule
from mailman.interfaces.usermanager import IUserManager
from public import public
from zope.component import getUtility
from zope.event import classhandler
from zope.interface import implementer

from mailman_pgp.config import config
from mailman_pgp.database import transaction
from mailman_pgp.model.address import PGPAddress
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.model.sighash import PGPSigHash
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.utils.email import get_email
from mailman_pgp.utils.moderation import record_action
from mailman_pgp.utils.pgp import expired, hashes, revoked, verifies


@public
@implementer(IRule)
class Signature:
    """The signature checking rule."""

    name = 'pgp-signature'
    description = _(
            'A rule which enforces PGP enabled list signature configuration.')
    record = False

    def check(self, mlist, msg, msgdata):
        """See `IRule`."""
        # Find the `PGPMailingList` this is for.
        pgp_list = PGPMailingList.for_list(mlist)
        if pgp_list is None:
            return False

        email = get_email(msg)
        # Wrap the message to work with it.
        wrapped = PGPWrapper(msg)

        # Take unsigned_msg_action if unsigned.
        if not wrapped.is_signed():
            action = pgp_list.unsigned_msg_action
            if action != Action.defer:
                record_action(msg, msgdata, action, email,
                              'The message is unsigned.')
                return True

        # Take `inline_pgp_action` if inline signed.
        if wrapped.inline.is_signed():
            action = pgp_list.inline_pgp_action
            if action != Action.defer:
                record_action(msg, msgdata, action, email,
                              'Inline PGP is not allowed.')
                return True

        # Lookup the address by sender, and its corresponding `PGPAddress`.
        user_manager = getUtility(IUserManager)
        address = user_manager.get_address(email)
        pgp_address = PGPAddress.for_address(address)
        if pgp_address is None:
            # Just let it continue.
            return False

        # See if we have a key.
        key = pgp_address.key
        if key is None:
            record_action(msg, msgdata, Action.reject, email,
                          'No key set for address {}.'.format(email))
            return True

        if not pgp_address.key_confirmed:
            record_action(msg, msgdata, Action.reject, email,
                          'Key not confirmed.')
            return True

        verifications = list(wrapped.verify(key))
        # verifications is a list of SignatureVerification, only contains
        # sigs that appear to be by the pgp_address.key

        if expired(verifications):
            action = pgp_list.expired_sig_action
            if action != Action.defer:
                record_action(msg, msgdata, action, email,
                              'Signature is expired.')
                return True

        if revoked(verifications):
            action = pgp_list.revoked_sig_action
            if action != Action.defer:
                record_action(msg, msgdata, action, email,
                              'Signature is made by a revoked key.')
                return True

        # Take the `invalid_sig_action` if the verification failed.
        if not verifies(verifications):
            action = pgp_list.invalid_sig_action
            if action != Action.defer:
                record_action(msg, msgdata, action, email,
                              'Signature did not verify.')
                return True

        sig_hashes = set(hashes(verifications))
        duplicates = set(PGPSigHash.hashes(sig_hashes))
        if duplicates:
            fingerprints = map(attrgetter('fingerprint'), duplicates)
            if key.fingerprint in fingerprints:
                action = pgp_list.duplicate_sig_action
                if action != Action.defer:
                    record_action(msg, msgdata, action, email,
                                  'Signature duplicate.')
                    return True
        msgdata['pgp_sig_hashes'] = sig_hashes

        return False


@classhandler.handler(AcceptEvent)
def on_message_posting(event):
    """
    Add sig hashes to sighash table.

    :param event:
    :type event: AcceptEvent
    """
    if not config.get_value('misc', 'collect_sig_hashes'):
        return
    pgp_list = PGPMailingList.for_list(event.mlist)
    if pgp_list is None:
        return
    address = getUtility(IUserManager).get_address(get_email(event.msg))
    pgp_address = PGPAddress.for_address(address)
    if pgp_address is None or pgp_address.key_fingerprint is None:
        return
    for sig_hash in event.msgdata['pgp_sig_hashes']:
        with transaction() as t:
            pgp_hash = PGPSigHash(hash=sig_hash,
                                  fingerprint=pgp_address.key_fingerprint)
            t.add(pgp_hash)
