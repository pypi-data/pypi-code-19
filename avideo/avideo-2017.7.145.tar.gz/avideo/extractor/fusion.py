
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
from .ooyala import OoyalaIE


class FusionIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?fusion\.net/video/(?P<id>\d+)'
    _TESTS = [{
        'url': 'http://fusion.net/video/201781/u-s-and-panamanian-forces-work-together-to-stop-a-vessel-smuggling-drugs/',
        'info_dict': {
            'id': 'ZpcWNoMTE6x6uVIIWYpHh0qQDjxBuq5P',
            'ext': 'mp4',
            'title': 'U.S. and Panamanian forces work together to stop a vessel smuggling drugs',
            'description': 'md5:0cc84a9943c064c0f46b128b41b1b0d7',
            'duration': 140.0,
        },
        'params': {
            'skip_download': True,
        },
        'add_ie': ['Ooyala'],
    }, {
        'url': 'http://fusion.net/video/201781',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        ooyala_code = self._search_regex(
            r'data-ooyala-id=(["\'])(?P<code>(?:(?!\1).)+)\1',
            webpage, 'ooyala code', group='code')

        return OoyalaIE._build_url_result(ooyala_code)
