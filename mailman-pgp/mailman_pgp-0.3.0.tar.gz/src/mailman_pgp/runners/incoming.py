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

"""The encryption-aware incoming runner."""
import logging

from mailman.config import config as mailman_config
from mailman.core.runner import Runner
from mailman.email.message import Message
from mailman.interfaces.action import Action
from mailman.model.mailinglist import MailingList
from pgpy.errors import PGPError
from public import public

from mailman_pgp.config import config
from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.wrapper import PGPWrapper
from mailman_pgp.utils.moderation import record_action

log = logging.getLogger('mailman.plugin.pgp')


def _pass_default(msg, msgdata, listid):
    inq = config.get_value('queues', 'in')
    mailman_config.switchboards[inq].enqueue(msg, msgdata,
                                             listid=listid)


@public
class PGPIncomingRunner(Runner):
    def _dispose(self, mlist: MailingList, msg: Message, msgdata: dict):
        """See `IRunner`."""
        # Is the message for an encrypted mailing list? If not, pass to default
        # incoming runner. If yes, go on.
        pgp_list = PGPMailingList.for_list(mlist)
        if not pgp_list:
            _pass_default(msg, msgdata, mlist.list_id)
            return False

        wrapped = PGPWrapper(msg)
        # Is the message encrypted?
        if wrapped.is_encrypted():
            # Decrypt it and pass it on.
            list_key = pgp_list.key
            if list_key is None:
                # keep the message and hope the key becomes available.
                return True

            try:
                msg = wrapped.decrypt(list_key).msg
            except PGPError:
                reason = 'Message could not be decrypted.'
                log.info('[pgp] {}{}: {}'.format(
                        Action.reject.name, msg.get('message-id', 'n/a'),
                        reason))
                record_action(msg, msgdata, Action.reject, msg.sender,
                              reason)
                msgdata['pgp_moderate'] = True
        else:
            # Take the `nonencrypted_msg_action`
            # just set some data for our `encryption` rule which will
            # jump to the moderation chain if `pgp_moderate` is True
            action = pgp_list.nonencrypted_msg_action
            if action != Action.defer:
                reason = 'Message was not encrypted.'
                log.info('[pgp] {}{}: {}'.format(
                        action.name, msg.get('message-id', 'n/a'), reason))
                record_action(msg, msgdata, action, msg.sender, reason)
                msgdata['pgp_moderate'] = True

        _pass_default(msg, msgdata, mlist.list_id)
        return False
