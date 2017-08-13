
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
    int_or_none,
)


class XXXYMoviesIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?xxxymovies\.com/videos/(?P<id>\d+)/(?P<display_id>[^/]+)'
    _TEST = {
        'url': 'http://xxxymovies.com/videos/138669/ecstatic-orgasm-sofcore/',
        'md5': '810b1bdbbffff89dd13bdb369fe7be4b',
        'info_dict': {
            'id': '138669',
            'display_id': 'ecstatic-orgasm-sofcore',
            'ext': 'mp4',
            'title': 'Ecstatic Orgasm Sofcore',
            'duration': 931,
            'categories': list,
            'view_count': int,
            'like_count': int,
            'dislike_count': int,
            'age_limit': 18,
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        display_id = mobj.group('display_id')

        webpage = self._download_webpage(url, display_id)

        video_url = self._search_regex(
            r"video_url\s*:\s*'([^']+)'", webpage, 'video URL')

        title = self._html_search_regex(
            [r'<div[^>]+\bclass="block_header"[^>]*>\s*<h1>([^<]+)<',
             r'<title>(.*?)\s*-\s*(?:XXXYMovies\.com|XXX\s+Movies)</title>'],
            webpage, 'title')

        thumbnail = self._search_regex(
            r"preview_url\s*:\s*'([^']+)'",
            webpage, 'thumbnail', fatal=False)

        categories = self._html_search_meta(
            'keywords', webpage, 'categories', default='').split(',')

        duration = parse_duration(self._search_regex(
            r'<span>Duration:</span>\s*(\d+:\d+)',
            webpage, 'duration', fatal=False))

        view_count = int_or_none(self._html_search_regex(
            r'<div class="video_views">\s*(\d+)',
            webpage, 'view count', fatal=False))
        like_count = int_or_none(self._search_regex(
            r'>\s*Likes? <b>\((\d+)\)',
            webpage, 'like count', fatal=False))
        dislike_count = int_or_none(self._search_regex(
            r'>\s*Dislike <b>\((\d+)\)</b>',
            webpage, 'dislike count', fatal=False))

        age_limit = self._rta_search(webpage)

        return {
            'id': video_id,
            'display_id': display_id,
            'url': video_url,
            'title': title,
            'thumbnail': thumbnail,
            'categories': categories,
            'duration': duration,
            'view_count': view_count,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'age_limit': age_limit,
        }
