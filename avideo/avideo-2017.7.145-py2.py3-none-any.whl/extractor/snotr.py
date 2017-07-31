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
from ..utils import (
    parse_duration,
    parse_filesize,
    str_to_int,
)


class SnotrIE(InfoExtractor):
    _VALID_URL = r'http?://(?:www\.)?snotr\.com/video/(?P<id>\d+)/([\w]+)'
    _TESTS = [{
        'url': 'http://www.snotr.com/video/13708/Drone_flying_through_fireworks',
        'info_dict': {
            'id': '13708',
            'ext': 'mp4',
            'title': 'Drone flying through fireworks!',
            'duration': 248,
            'filesize_approx': 40700000,
            'description': 'A drone flying through Fourth of July Fireworks',
            'thumbnail': r're:^https?://.*\.jpg$',
        },
        'expected_warnings': ['description'],
    }, {
        'url': 'http://www.snotr.com/video/530/David_Letteman_-_George_W_Bush_Top_10',
        'info_dict': {
            'id': '530',
            'ext': 'mp4',
            'title': 'David Letteman - George W. Bush Top 10',
            'duration': 126,
            'filesize_approx': 8500000,
            'description': 'The top 10 George W. Bush moments, brought to you by David Letterman!',
            'thumbnail': r're:^https?://.*\.jpg$',
        }
    }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')

        webpage = self._download_webpage(url, video_id)
        title = self._og_search_title(webpage)

        description = self._og_search_description(webpage)
        info_dict = self._parse_html5_media_entries(
            url, webpage, video_id, m3u8_entry_protocol='m3u8_native')[0]

        view_count = str_to_int(self._html_search_regex(
            r'<p[^>]*>\s*<strong[^>]*>Views:</strong>\s*<span[^>]*>([\d,\.]+)',
            webpage, 'view count', fatal=False))

        duration = parse_duration(self._html_search_regex(
            r'<p[^>]*>\s*<strong[^>]*>Length:</strong>\s*<span[^>]*>([\d:]+)',
            webpage, 'duration', fatal=False))

        filesize_approx = parse_filesize(self._html_search_regex(
            r'<p[^>]*>\s*<strong[^>]*>Filesize:</strong>\s*<span[^>]*>([^<]+)',
            webpage, 'filesize', fatal=False))

        info_dict.update({
            'id': video_id,
            'description': description,
            'title': title,
            'view_count': view_count,
            'duration': duration,
            'filesize_approx': filesize_approx,
        })

        return info_dict
