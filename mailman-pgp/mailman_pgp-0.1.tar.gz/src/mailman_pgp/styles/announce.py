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

from mailman.styles.default import LegacyAnnounceOnly
from public import public

from mailman_pgp.styles.base import PGPStyle


@public
class AnnounceStyle(LegacyAnnounceOnly, PGPStyle):
    name = 'pgp-announce'
    description = 'Announce only PGP enabled mailing list style.'

    def apply(self, mailing_list):
        """See `IStyle`."""
        LegacyAnnounceOnly.apply(self, mailing_list)
        PGPStyle.apply(self, mailing_list)
