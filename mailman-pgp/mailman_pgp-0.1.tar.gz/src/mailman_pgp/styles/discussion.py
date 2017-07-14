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

from mailman.styles.default import LegacyDefaultStyle
from public import public

from mailman_pgp.styles.base import PGPStyle


@public
class DiscussionStyle(LegacyDefaultStyle, PGPStyle):
    name = 'pgp-default'
    description = 'Ordinary discussion PGP enabled mailing list style.'

    def apply(self, mailing_list):
        """See `IStyle`."""
        LegacyDefaultStyle.apply(self, mailing_list)
        PGPStyle.apply(self, mailing_list)
