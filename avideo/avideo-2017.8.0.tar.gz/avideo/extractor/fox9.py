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

from .anvato import AnvatoIE
from ..utils import js_to_json


class FOX9IE(AnvatoIE):
    _VALID_URL = r'https?://(?:www\.)?fox9\.com/(?:[^/]+/)+(?P<id>\d+)-story'
    _TESTS = [{
        'url': 'http://www.fox9.com/news/215123287-story',
        'md5': 'd6e1b2572c3bab8a849c9103615dd243',
        'info_dict': {
            'id': '314473',
            'ext': 'mp4',
            'title': 'Bear climbs tree in downtown Duluth',
            'description': 'md5:6a36bfb5073a411758a752455408ac90',
            'duration': 51,
            'timestamp': 1478123580,
            'upload_date': '20161102',
            'uploader': 'EPFOX',
            'categories': ['News', 'Sports'],
            'tags': ['news', 'video'],
        },
    }, {
        'url': 'http://www.fox9.com/news/investigators/214070684-story',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        video_id = self._parse_json(
            self._search_regex(
                r'AnvatoPlaylist\s*\(\s*(\[.+?\])\s*\)\s*;',
                webpage, 'anvato playlist'),
            video_id, transform_source=js_to_json)[0]['video']

        return self._get_anvato_videos(
            'anvato_epfox_app_web_prod_b3373168e12f423f41504f207000188daf88251b',
            video_id)
