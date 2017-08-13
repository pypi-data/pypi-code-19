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
from ..compat import compat_urllib_parse_unquote


class XNXXIE(InfoExtractor):
    _VALID_URL = r'https?://(?:video|www)\.xnxx\.com/video-?(?P<id>[0-9a-z]+)/'
    _TESTS = [{
        'url': 'http://www.xnxx.com/video-55awb78/skyrim_test_video',
        'md5': 'ef7ecee5af78f8b03dca2cf31341d3a0',
        'info_dict': {
            'id': '55awb78',
            'ext': 'flv',
            'title': 'Skyrim Test Video',
            'age_limit': 18,
        },
    }, {
        'url': 'http://video.xnxx.com/video1135332/lida_naked_funny_actress_5_',
        'only_matching': True,
    }, {
        'url': 'http://www.xnxx.com/video-55awb78/',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        video_url = self._search_regex(r'flv_url=(.*?)&amp;',
                                       webpage, 'video URL')
        video_url = compat_urllib_parse_unquote(video_url)

        video_title = self._html_search_regex(r'<title>(.*?)\s+-\s+XNXX.COM',
                                              webpage, 'title')

        video_thumbnail = self._search_regex(r'url_bigthumb=(.*?)&amp;',
                                             webpage, 'thumbnail', fatal=False)

        return {
            'id': video_id,
            'url': video_url,
            'title': video_title,
            'ext': 'flv',
            'thumbnail': video_thumbnail,
            'age_limit': 18,
        }
