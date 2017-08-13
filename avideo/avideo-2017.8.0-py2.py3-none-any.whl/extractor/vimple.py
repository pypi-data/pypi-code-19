
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
from ..utils import int_or_none


class SprutoBaseIE(InfoExtractor):
    def _extract_spruto(self, spruto, video_id):
        playlist = spruto['playlist'][0]
        title = playlist['title']
        video_id = playlist.get('videoId') or video_id
        thumbnail = playlist.get('posterUrl') or playlist.get('thumbnailUrl')
        duration = int_or_none(playlist.get('duration'))

        formats = [{
            'url': f['url'],
        } for f in playlist['video']]
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'formats': formats,
        }


class VimpleIE(SprutoBaseIE):
    IE_DESC = 'Vimple - one-click video hosting'
    _VALID_URL = r'https?://(?:player\.vimple\.(?:ru|co)/iframe|vimple\.(?:ru|co))/(?P<id>[\da-f-]{32,36})'
    _TESTS = [{
        'url': 'http://vimple.ru/c0f6b1687dcd4000a97ebe70068039cf',
        'md5': '2e750a330ed211d3fd41821c6ad9a279',
        'info_dict': {
            'id': 'c0f6b168-7dcd-4000-a97e-be70068039cf',
            'ext': 'mp4',
            'title': 'Sunset',
            'duration': 20,
            'thumbnail': r're:https?://.*?\.jpg',
        },
    }, {
        'url': 'http://player.vimple.ru/iframe/52e1beec-1314-4a83-aeac-c61562eadbf9',
        'only_matching': True,
    }, {
        'url': 'http://vimple.co/04506a053f124483b8fb05ed73899f19',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(
            'http://player.vimple.ru/iframe/%s' % video_id, video_id)

        spruto = self._parse_json(
            self._search_regex(
                r'sprutoData\s*:\s*({.+?}),\r\n', webpage, 'spruto data'),
            video_id)

        return self._extract_spruto(spruto, video_id)
