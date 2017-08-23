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

from mailman.interfaces.handler import IHandler
from public import public
from zope.interface import implementer

from mailman_pgp.model.list import PGPMailingList
from mailman_pgp.pgp.wrapper import PGPWrapper


@public
@implementer(IHandler)
class SignatureStrip:
    name = 'pgp-signature-strip'
    description = 'Strip the signature of the message.'

    def process(self, mlist, msg, msgdata):
        """See `IHandler`."""
        pgp_list = PGPMailingList.for_list(mlist)
        if not pgp_list or not pgp_list.strip_original_sig:
            return

        PGPWrapper(msg).strip_signature()
