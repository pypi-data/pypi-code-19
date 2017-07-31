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

import random

from .common import InfoExtractor
from ..utils import xpath_text


class MatchTVIE(InfoExtractor):
    _VALID_URL = r'https?://matchtv\.ru(?:/on-air|/?#live-player)'
    _TESTS = [{
        'url': 'http://matchtv.ru/#live-player',
        'info_dict': {
            'id': 'matchtv-live',
            'ext': 'flv',
            'title': r're:^Матч ТВ - Прямой эфир \d{4}-\d{2}-\d{2} \d{2}:\d{2}$',
            'is_live': True,
        },
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'http://matchtv.ru/on-air/',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = 'matchtv-live'
        video_url = self._download_json(
            'http://player.matchtv.ntvplus.tv/player/smil', video_id,
            query={
                'ts': '',
                'quality': 'SD',
                'contentId': '561d2c0df7159b37178b4567',
                'sign': '',
                'includeHighlights': '0',
                'userId': '',
                'sessionId': random.randint(1, 1000000000),
                'contentType': 'channel',
                'timeShift': '0',
                'platform': 'portal',
            },
            headers={
                'Referer': 'http://player.matchtv.ntvplus.tv/embed-player/NTVEmbedPlayer.swf',
            })['data']['videoUrl']
        f4m_url = xpath_text(self._download_xml(video_url, video_id), './to')
        formats = self._extract_f4m_formats(f4m_url, video_id)
        self._sort_formats(formats)
        return {
            'id': video_id,
            'title': self._live_title('Матч ТВ - Прямой эфир'),
            'is_live': True,
            'formats': formats,
        }
