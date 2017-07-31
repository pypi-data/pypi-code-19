# coding: utf-8

# Copyright (C) 2017 avideo authors (see AUTHORS)

#
#    This file is part of avideo.
#
#    avideo is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    avideo is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with avideo.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    extract_attributes,
)


class NZZIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?nzz\.ch/(?:[^/]+/)*[^/?#]+-ld\.(?P<id>\d+)'
    _TEST = {
        'url': 'http://www.nzz.ch/zuerich/gymizyte/gymizyte-schreiben-schueler-heute-noch-diktate-ld.9153',
        'info_dict': {
            'id': '9153',
        },
        'playlist_mincount': 6,
    }

    def _real_extract(self, url):
        page_id = self._match_id(url)
        webpage = self._download_webpage(url, page_id)

        entries = []
        for player_element in re.findall(r'(<[^>]+class="kalturaPlayer"[^>]*>)', webpage):
            player_params = extract_attributes(player_element)
            if player_params.get('data-type') not in ('kaltura_singleArticle',):
                self.report_warning('Unsupported player type')
                continue
            entry_id = player_params['data-id']
            entries.append(self.url_result(
                'kaltura:1750922:' + entry_id, 'Kaltura', entry_id))

        return self.playlist_result(entries, page_id)
