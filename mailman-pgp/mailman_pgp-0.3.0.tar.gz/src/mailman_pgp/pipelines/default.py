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
from mailman.pipelines.base import BasePipeline

from public import public


@public
class PGPPostingPipeline(BasePipeline):
    """The built-in owner pipeline."""

    name = 'pgp-posting-pipeline'
    description = 'PGP posting pipeline'

    _default_handlers = (
        'pgp-signature-strip',
        'mime-delete',
        'tagger',
        'member-recipients',
        'avoid-duplicates',
        'cleanse',
        'cleanse-dkim',
        'cook-headers',
        'subject-prefix',
        'rfc-2369',
        'to-archive',
        'to-digest',
        'to-usenet',
        'after-delivery',
        'acknowledge',
        'decorate',
        'dmarc',
        'to-outgoing',
    )
