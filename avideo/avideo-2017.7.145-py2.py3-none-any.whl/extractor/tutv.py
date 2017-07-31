
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

import base64

from .common import InfoExtractor
from ..compat import compat_parse_qs


class TutvIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?tu\.tv/videos/(?P<id>[^/?]+)'
    _TEST = {
        'url': 'http://tu.tv/videos/robots-futbolistas',
        'md5': '0cd9e28ad270488911b0d2a72323395d',
        'info_dict': {
            'id': '2973058',
            'ext': 'mp4',
            'title': 'Robots futbolistas',
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        internal_id = self._search_regex(r'codVideo=([0-9]+)', webpage, 'internal video ID')

        data_content = self._download_webpage(
            'http://tu.tv/flvurl.php?codVideo=%s' % internal_id, video_id, 'Downloading video info')
        video_url = base64.b64decode(compat_parse_qs(data_content)['kpt'][0].encode('utf-8')).decode('utf-8')

        return {
            'id': internal_id,
            'url': video_url,
            'title': self._og_search_title(webpage),
        }
