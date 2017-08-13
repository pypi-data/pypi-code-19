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
    int_or_none,
    parse_duration,
)


class HornBunnyIE(InfoExtractor):
    _VALID_URL = r'http?://(?:www\.)?hornbunny\.com/videos/(?P<title_dash>[a-z-]+)-(?P<id>\d+)\.html'
    _TEST = {
        'url': 'http://hornbunny.com/videos/panty-slut-jerk-off-instruction-5227.html',
        'md5': 'e20fd862d1894b67564c96f180f43924',
        'info_dict': {
            'id': '5227',
            'ext': 'mp4',
            'title': 'panty slut jerk off instruction',
            'duration': 550,
            'age_limit': 18,
            'view_count': int,
            'thumbnail': r're:^https?://.*\.jpg$',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)
        title = self._og_search_title(webpage)
        info_dict = self._parse_html5_media_entries(url, webpage, video_id)[0]

        duration = parse_duration(self._search_regex(
            r'<strong>Runtime:</strong>\s*([0-9:]+)</div>',
            webpage, 'duration', fatal=False))
        view_count = int_or_none(self._search_regex(
            r'<strong>Views:</strong>\s*(\d+)</div>',
            webpage, 'view count', fatal=False))

        info_dict.update({
            'id': video_id,
            'title': title,
            'duration': duration,
            'view_count': view_count,
            'age_limit': 18,
        })

        return info_dict
