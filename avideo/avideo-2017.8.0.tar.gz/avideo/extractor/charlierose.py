
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
from ..utils import remove_end


class CharlieRoseIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?charlierose\.com/video(?:s|/player)/(?P<id>\d+)'
    _TESTS = [{
        'url': 'https://charlierose.com/videos/27996',
        'md5': 'fda41d49e67d4ce7c2411fd2c4702e09',
        'info_dict': {
            'id': '27996',
            'ext': 'mp4',
            'title': 'Remembering Zaha Hadid',
            'thumbnail': r're:^https?://.*\.jpg\?\d+',
            'description': 'We revisit past conversations with Zaha Hadid, in memory of the world renowned Iraqi architect.',
            'subtitles': {
                'en': [{
                    'ext': 'vtt',
                }],
            },
        },
    }, {
        'url': 'https://charlierose.com/videos/27996',
        'only_matching': True,
    }]

    _PLAYER_BASE = 'https://charlierose.com/video/player/%s'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(self._PLAYER_BASE % video_id, video_id)

        title = remove_end(self._og_search_title(webpage), ' - Charlie Rose')

        info_dict = self._parse_html5_media_entries(
            self._PLAYER_BASE % video_id, webpage, video_id,
            m3u8_entry_protocol='m3u8_native')[0]

        self._sort_formats(info_dict['formats'])
        self._remove_duplicate_formats(info_dict['formats'])

        info_dict.update({
            'id': video_id,
            'title': title,
            'thumbnail': self._og_search_thumbnail(webpage),
            'description': self._og_search_description(webpage),
        })

        return info_dict
