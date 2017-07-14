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

"""Encryption moderation rule for the pgp-posting-chain."""

from mailman.core.i18n import _
from mailman.interfaces.rules import IRule
from public.public import public
from zope.interface import implementer


@public
@implementer(IRule)
class Encryption:
    """The encryption moderation rule."""

    name = 'encryption'
    description = _(
            "A rule which jumps to the moderation chain, "
            "when the incoming runner instructs it to.")
    record = True

    def check(self, mlist, msg, msgdata):
        """See `IRule`."""
        return msgdata.get('pgp_moderate', False)
