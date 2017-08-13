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
    compat_parse_qs,
)
from ..utils import (
    parse_duration,
)


class GoshgayIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?goshgay\.com/video(?P<id>\d+?)($|/)'
    _TEST = {
        'url': 'http://www.goshgay.com/video299069/diesel_sfw_xxx_video',
        'md5': '4b6db9a0a333142eb9f15913142b0ed1',
        'info_dict': {
            'id': '299069',
            'ext': 'flv',
            'title': 'DIESEL SFW XXX Video',
            'thumbnail': r're:^http://.*\.jpg$',
            'duration': 80,
            'age_limit': 18,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        title = self._html_search_regex(
            r'<h2>(.*?)<', webpage, 'title')
        duration = parse_duration(self._html_search_regex(
            r'<span class="duration">\s*-?\s*(.*?)</span>',
            webpage, 'duration', fatal=False))

        flashvars = compat_parse_qs(self._html_search_regex(
            r'<embed.+?id="flash-player-embed".+?flashvars="([^"]+)"',
            webpage, 'flashvars'))
        thumbnail = flashvars.get('url_bigthumb', [None])[0]
        video_url = flashvars['flv_url'][0]

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'age_limit': 18,
        }
