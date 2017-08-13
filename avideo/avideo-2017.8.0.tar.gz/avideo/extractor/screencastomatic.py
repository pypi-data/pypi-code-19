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
from ..utils import js_to_json


class ScreencastOMaticIE(InfoExtractor):
    _VALID_URL = r'https?://screencast-o-matic\.com/watch/(?P<id>[0-9a-zA-Z]+)'
    _TEST = {
        'url': 'http://screencast-o-matic.com/watch/c2lD3BeOPl',
        'md5': '483583cb80d92588f15ccbedd90f0c18',
        'info_dict': {
            'id': 'c2lD3BeOPl',
            'ext': 'mp4',
            'title': 'Welcome to 3-4 Philosophy @ DECV!',
            'thumbnail': r're:^https?://.*\.jpg$',
            'description': 'as the title says! also: some general info re 1) VCE philosophy and 2) distance learning.',
            'duration': 369.163,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        jwplayer_data = self._parse_json(
            self._search_regex(
                r"(?s)jwplayer\('mp4Player'\).setup\((\{.*?\})\);", webpage, 'setup code'),
            video_id, transform_source=js_to_json)

        info_dict = self._parse_jwplayer_data(jwplayer_data, video_id, require_title=False)
        info_dict.update({
            'title': self._og_search_title(webpage),
            'description': self._og_search_description(webpage),
        })
        return info_dict
