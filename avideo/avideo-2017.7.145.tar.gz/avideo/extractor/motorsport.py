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
from ..compat import (
    compat_urlparse,
)


class MotorsportIE(InfoExtractor):
    IE_DESC = 'motorsport.com'
    _VALID_URL = r'https?://(?:www\.)?motorsport\.com/[^/?#]+/video/(?:[^/?#]+/)(?P<id>[^/]+)/?(?:$|[?#])'
    _TEST = {
        'url': 'http://www.motorsport.com/f1/video/main-gallery/red-bull-racing-2014-rules-explained/',
        'info_dict': {
            'id': '2-T3WuR-KMM',
            'ext': 'mp4',
            'title': 'Red Bull Racing: 2014 Rules Explained',
            'duration': 208,
            'description': 'A new clip from Red Bull sees Daniel Ricciardo and Sebastian Vettel explain the 2014 Formula One regulations – which are arguably the most complex the sport has ever seen.',
            'uploader': 'mcomstaff',
            'uploader_id': 'UC334JIYKkVnyFoNCclfZtHQ',
            'upload_date': '20140903',
            'thumbnail': r're:^https?://.+\.jpg$'
        },
        'add_ie': ['Youtube'],
        'params': {
            'skip_download': True,
        },
    }

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        iframe_path = self._html_search_regex(
            r'<iframe id="player_iframe"[^>]+src="([^"]+)"', webpage,
            'iframe path')
        iframe = self._download_webpage(
            compat_urlparse.urljoin(url, iframe_path), display_id,
            'Downloading iframe')
        youtube_id = self._search_regex(
            r'www.youtube.com/embed/(.{11})', iframe, 'youtube id')

        return {
            '_type': 'url_transparent',
            'display_id': display_id,
            'url': 'https://youtube.com/watch?v=%s' % youtube_id,
        }
