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

"""The encryption-aware outgoing runner"""

from mailman.config import config as mailman_config
from mailman.core.runner import Runner
from mailman.email.message import Message
from mailman.model.mailinglist import MailingList
from public import public

from mailman_pgp.config import config
from mailman_pgp.model.list import PGPMailingList


@public
class OutgoingRunner(Runner):
    def _dispose(self, mlist: MailingList, msg: Message, msgdata: dict):
        """See `IRunner`."""
        pgp_list = PGPMailingList.for_list(mlist)
        if not pgp_list:
            outq = config.get('queues', 'out')
            mailman_config.switchboards[outq].enqueue(msg,
                                                      msgdata,
                                                      listid=mlist.list_id)
        return False
