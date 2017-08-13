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
from ..utils import parse_duration


class WatchIndianPornIE(InfoExtractor):
    IE_DESC = 'Watch Indian Porn'
    _VALID_URL = r'https?://(?:www\.)?watchindianporn\.net/(?:[^/]+/)*video/(?P<display_id>[^/]+)-(?P<id>[a-zA-Z0-9]+)\.html'
    _TEST = {
        'url': 'http://www.watchindianporn.net/video/hot-milf-from-kerala-shows-off-her-gorgeous-large-breasts-on-camera-RZa2avywNPa.html',
        'md5': '249589a164dde236ec65832bfce17440',
        'info_dict': {
            'id': 'RZa2avywNPa',
            'display_id': 'hot-milf-from-kerala-shows-off-her-gorgeous-large-breasts-on-camera',
            'ext': 'mp4',
            'title': 'Hot milf from kerala shows off her gorgeous large breasts on camera',
            'thumbnail': r're:^https?://.*\.jpg$',
            'duration': 226,
            'view_count': int,
            'categories': list,
            'age_limit': 18,
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        display_id = mobj.group('display_id')

        webpage = self._download_webpage(url, display_id)

        info_dict = self._parse_html5_media_entries(url, webpage, video_id)[0]

        title = self._html_search_regex((
            r'<title>(.+?)\s*-\s*Indian\s+Porn</title>',
            r'<h4>(.+?)</h4>'
        ), webpage, 'title')

        duration = parse_duration(self._search_regex(
            r'Time:\s*<strong>\s*(.+?)\s*</strong>',
            webpage, 'duration', fatal=False))

        view_count = int(self._search_regex(
            r'(?s)Time:\s*<strong>.*?</strong>.*?<strong>\s*(\d+)\s*</strong>',
            webpage, 'view count', fatal=False))

        categories = re.findall(
            r'<a[^>]+class=[\'"]categories[\'"][^>]*>\s*([^<]+)\s*</a>',
            webpage)

        info_dict.update({
            'id': video_id,
            'display_id': display_id,
            'http_headers': {
                'Referer': url,
            },
            'title': title,
            'duration': duration,
            'view_count': view_count,
            'categories': categories,
            'age_limit': 18,
        })

        return info_dict
