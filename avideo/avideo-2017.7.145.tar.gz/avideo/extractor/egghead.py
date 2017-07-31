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

import re

from .common import InfoExtractor


class EggheadCourseIE(InfoExtractor):
    IE_DESC = 'egghead.io course'
    IE_NAME = 'egghead:course'
    _VALID_URL = r'https://egghead\.io/courses/(?P<id>[a-zA-Z_0-9-]+)'
    _TEST = {
        'url': 'https://egghead.io/courses/professor-frisby-introduces-composable-functional-javascript',
        'playlist_count': 29,
        'info_dict': {
            'id': 'professor-frisby-introduces-composable-functional-javascript',
            'title': 'Professor Frisby Introduces Composable Functional JavaScript',
            'description': 're:(?s)^This course teaches the ubiquitous.*You\'ll start composing functionality before you know it.$',
        },
    }

    def _real_extract(self, url):
        playlist_id = self._match_id(url)
        webpage = self._download_webpage(url, playlist_id)

        title = self._html_search_regex(r'<h1 class="title">([^<]+)</h1>', webpage, 'title')
        ul = self._search_regex(r'(?s)<ul class="series-lessons-list">(.*?)</ul>', webpage, 'session list')

        found = re.findall(r'(?s)<a class="[^"]*"\s*href="([^"]+)">\s*<li class="item', ul)
        entries = [self.url_result(m) for m in found]

        return {
            '_type': 'playlist',
            'id': playlist_id,
            'title': title,
            'description': self._og_search_description(webpage),
            'entries': entries,
        }
