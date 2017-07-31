
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
from .ooyala import OoyalaIE


class TeachingChannelIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?teachingchannel\.org/videos/(?P<title>.+)'

    _TEST = {
        'url': 'https://www.teachingchannel.org/videos/teacher-teaming-evolution',
        'md5': '3d6361864d7cac20b57c8784da17166f',
        'info_dict': {
            'id': 'F3bnlzbToeI6pLEfRyrlfooIILUjz4nM',
            'ext': 'mp4',
            'title': 'A History of Teaming',
            'description': 'md5:2a9033db8da81f2edffa4c99888140b3',
            'duration': 422.255,
        },
        'params': {
            'skip_download': True,
        },
        'add_ie': ['Ooyala'],
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        title = mobj.group('title')
        webpage = self._download_webpage(url, title)
        ooyala_code = self._search_regex(
            r'data-embed-code=\'(.+?)\'', webpage, 'ooyala code')

        return OoyalaIE._build_url_result(ooyala_code)
