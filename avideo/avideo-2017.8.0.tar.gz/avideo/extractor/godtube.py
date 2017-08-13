
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
    parse_duration,
    parse_iso8601,
)


class GodTubeIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?godtube\.com/watch/\?v=(?P<id>[\da-zA-Z]+)'
    _TESTS = [
        {
            'url': 'https://www.godtube.com/watch/?v=0C0CNNNU',
            'md5': '77108c1e4ab58f48031101a1a2119789',
            'info_dict': {
                'id': '0C0CNNNU',
                'ext': 'mp4',
                'title': 'Woman at the well.',
                'duration': 159,
                'timestamp': 1205712000,
                'uploader': 'beverlybmusic',
                'upload_date': '20080317',
                'thumbnail': r're:^https?://.*\.jpg$',
            },
        },
    ]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')

        config = self._download_xml(
            'http://www.godtube.com/resource/mediaplayer/%s.xml' % video_id.lower(),
            video_id, 'Downloading player config XML')

        video_url = config.find('file').text
        uploader = config.find('author').text
        timestamp = parse_iso8601(config.find('date').text)
        duration = parse_duration(config.find('duration').text)
        thumbnail = config.find('image').text

        media = self._download_xml(
            'http://www.godtube.com/media/xml/?v=%s' % video_id, video_id, 'Downloading media XML')

        title = media.find('title').text

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'thumbnail': thumbnail,
            'timestamp': timestamp,
            'uploader': uploader,
            'duration': duration,
        }
