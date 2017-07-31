
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

from .common import InfoExtractor
from ..utils import parse_duration


class DHMIE(InfoExtractor):
    IE_DESC = 'Filmarchiv - Deutsches Historisches Museum'
    _VALID_URL = r'https?://(?:www\.)?dhm\.de/filmarchiv/(?:[^/]+/)+(?P<id>[^/]+)'

    _TESTS = [{
        'url': 'http://www.dhm.de/filmarchiv/die-filme/the-marshallplan-at-work-in-west-germany/',
        'md5': '11c475f670209bf6acca0b2b7ef51827',
        'info_dict': {
            'id': 'the-marshallplan-at-work-in-west-germany',
            'ext': 'flv',
            'title': 'MARSHALL PLAN AT WORK IN WESTERN GERMANY, THE',
            'description': 'md5:1fabd480c153f97b07add61c44407c82',
            'duration': 660,
            'thumbnail': r're:^https?://.*\.jpg$',
        },
    }, {
        'url': 'http://www.dhm.de/filmarchiv/02-mapping-the-wall/peter-g/rolle-1/',
        'md5': '09890226332476a3e3f6f2cb74734aa5',
        'info_dict': {
            'id': 'rolle-1',
            'ext': 'flv',
            'title': 'ROLLE 1',
            'thumbnail': r're:^https?://.*\.jpg$',
        },
    }]

    def _real_extract(self, url):
        playlist_id = self._match_id(url)

        webpage = self._download_webpage(url, playlist_id)

        playlist_url = self._search_regex(
            r"file\s*:\s*'([^']+)'", webpage, 'playlist url')

        entries = self._extract_xspf_playlist(playlist_url, playlist_id)

        title = self._search_regex(
            [r'dc:title="([^"]+)"', r'<title> &raquo;([^<]+)</title>'],
            webpage, 'title').strip()
        description = self._html_search_regex(
            r'<p><strong>Description:</strong>(.+?)</p>',
            webpage, 'description', default=None)
        duration = parse_duration(self._search_regex(
            r'<em>Length\s*</em>\s*:\s*</strong>([^<]+)',
            webpage, 'duration', default=None))

        entries[0].update({
            'title': title,
            'description': description,
            'duration': duration,
        })

        return self.playlist_result(entries, playlist_id)
