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
from ..utils import (
    ExtractorError,
    HEADRequest,
)


class AparatIE(InfoExtractor):
    _VALID_URL = r'^https?://(?:www\.)?aparat\.com/(?:v/|video/video/embed/videohash/)(?P<id>[a-zA-Z0-9]+)'

    _TEST = {
        'url': 'http://www.aparat.com/v/wP8On',
        'md5': '131aca2e14fe7c4dcb3c4877ba300c89',
        'info_dict': {
            'id': 'wP8On',
            'ext': 'mp4',
            'title': 'تیم گلکسی 11 - زومیت',
            'age_limit': 0,
        },
        # 'skip': 'Extremely unreliable',
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        # Note: There is an easier-to-parse configuration at
        # http://www.aparat.com/video/video/config/videohash/%video_id
        # but the URL in there does not work
        embed_url = 'http://www.aparat.com/video/video/embed/vt/frame/showvideo/yes/videohash/' + video_id
        webpage = self._download_webpage(embed_url, video_id)

        file_list = self._parse_json(self._search_regex(
            r'fileList\s*=\s*JSON\.parse\(\'([^\']+)\'\)', webpage, 'file list'), video_id)
        for i, item in enumerate(file_list[0]):
            video_url = item['file']
            req = HEADRequest(video_url)
            res = self._request_webpage(
                req, video_id, note='Testing video URL %d' % i, errnote=False)
            if res:
                break
        else:
            raise ExtractorError('No working video URLs found')

        title = self._search_regex(r'\s+title:\s*"([^"]+)"', webpage, 'title')
        thumbnail = self._search_regex(
            r'image:\s*"([^"]+)"', webpage, 'thumbnail', fatal=False)

        return {
            'id': video_id,
            'title': title,
            'url': video_url,
            'ext': 'mp4',
            'thumbnail': thumbnail,
            'age_limit': self._family_friendly_search(webpage),
        }
