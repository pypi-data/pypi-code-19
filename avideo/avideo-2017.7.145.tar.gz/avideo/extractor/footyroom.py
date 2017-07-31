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

from .common import InfoExtractor
from .streamable import StreamableIE


class FootyRoomIE(InfoExtractor):
    _VALID_URL = r'https?://footyroom\.com/matches/(?P<id>\d+)'
    _TESTS = [{
        'url': 'http://footyroom.com/matches/79922154/hull-city-vs-chelsea/review',
        'info_dict': {
            'id': '79922154',
            'title': 'VIDEO Hull City 0 - 2 Chelsea',
        },
        'playlist_count': 2,
        'add_ie': [StreamableIE.ie_key()],
    }, {
        'url': 'http://footyroom.com/matches/75817984/georgia-vs-germany/review',
        'info_dict': {
            'id': '75817984',
            'title': 'VIDEO Georgia 0 - 2 Germany',
        },
        'playlist_count': 1,
        'add_ie': ['Playwire']
    }]

    def _real_extract(self, url):
        playlist_id = self._match_id(url)

        webpage = self._download_webpage(url, playlist_id)

        playlist = self._parse_json(self._search_regex(
            r'DataStore\.media\s*=\s*([^;]+)', webpage, 'media data'),
            playlist_id)

        playlist_title = self._og_search_title(webpage)

        entries = []
        for video in playlist:
            payload = video.get('payload')
            if not payload:
                continue
            playwire_url = self._html_search_regex(
                r'data-config="([^"]+)"', payload,
                'playwire url', default=None)
            if playwire_url:
                entries.append(self.url_result(self._proto_relative_url(
                    playwire_url, 'http:'), 'Playwire'))

            streamable_url = StreamableIE._extract_url(payload)
            if streamable_url:
                entries.append(self.url_result(
                    streamable_url, StreamableIE.ie_key()))

        return self.playlist_result(entries, playlist_id, playlist_title)
