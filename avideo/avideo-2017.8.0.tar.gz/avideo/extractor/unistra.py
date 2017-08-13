
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
from ..utils import qualities


class UnistraIE(InfoExtractor):
    _VALID_URL = r'https?://utv\.unistra\.fr/(?:index|video)\.php\?id_video\=(?P<id>\d+)'

    _TESTS = [
        {
            'url': 'http://utv.unistra.fr/video.php?id_video=154',
            'md5': '736f605cfdc96724d55bb543ab3ced24',
            'info_dict': {
                'id': '154',
                'ext': 'mp4',
                'title': 'M!ss Yella',
                'description': 'md5:104892c71bd48e55d70b902736b81bbf',
            },
        },
        {
            'url': 'http://utv.unistra.fr/index.php?id_video=437',
            'md5': '1ddddd6cccaae76f622ce29b8779636d',
            'info_dict': {
                'id': '437',
                'ext': 'mp4',
                'title': 'Prix Louise Weiss 2014',
                'description': 'md5:cc3a8735f079f4fb6b0b570fc10c135a',
            },
        }
    ]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')

        webpage = self._download_webpage(url, video_id)

        files = set(re.findall(r'file\s*:\s*"(/[^"]+)"', webpage))

        quality = qualities(['SD', 'HD'])
        formats = []
        for file_path in files:
            format_id = 'HD' if file_path.endswith('-HD.mp4') else 'SD'
            formats.append({
                'url': 'http://vod-flash.u-strasbg.fr:8080%s' % file_path,
                'format_id': format_id,
                'quality': quality(format_id)
            })
        self._sort_formats(formats)

        title = self._html_search_regex(
            r'<title>UTV - (.*?)</', webpage, 'title')
        description = self._html_search_regex(
            r'<meta name="Description" content="(.*?)"', webpage, 'description', flags=re.DOTALL)
        thumbnail = self._search_regex(
            r'image: "(.*?)"', webpage, 'thumbnail')

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'formats': formats
        }
