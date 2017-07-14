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

"""A PGP enabled posting chain."""

from mailman.chains.base import Link
from mailman.core.i18n import _
from mailman.interfaces.chain import IChain, LinkAction
from public import public
from zope.interface import implementer


@public
@implementer(IChain)
class PGPChain:
    """Default PGP chain."""

    name = 'pgp-posting-chain'
    description = _('The PGP enabled moderation chain.')

    _link_descriptions = (
        ('encryption', LinkAction.jump, 'moderation'),
        ('signature', LinkAction.jump, 'moderation'),
        ('truth', LinkAction.jump, 'default-posting-chain')
    )

    def __init__(self):
        self._cached_links = None

    def get_links(self, mlist, msg, msgdata):
        """See `IChain`."""
        if self._cached_links is None:
            self._cached_links = links = []
            for rule, action, chain in self._link_descriptions:
                links.append(Link(rule, action, chain))
        return iter(self._cached_links)
