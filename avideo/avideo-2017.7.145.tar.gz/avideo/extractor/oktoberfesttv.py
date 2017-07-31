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


class OktoberfestTVIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?oktoberfest-tv\.de/[^/]+/[^/]+/video/(?P<id>[^/?#]+)'

    _TEST = {
        'url': 'http://www.oktoberfest-tv.de/de/kameras/video/hb-zelt',
        'info_dict': {
            'id': 'hb-zelt',
            'ext': 'mp4',
            'title': 're:^Live-Kamera: Hofbräuzelt [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$',
            'thumbnail': r're:^https?://.*\.jpg$',
            'is_live': True,
        },
        'params': {
            'skip_download': True,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        title = self._live_title(self._html_search_regex(
            r'<h1><strong>.*?</strong>(.*?)</h1>', webpage, 'title'))

        clip = self._search_regex(
            r"clip:\s*\{\s*url:\s*'([^']+)'", webpage, 'clip')
        ncurl = self._search_regex(
            r"netConnectionUrl:\s*'([^']+)'", webpage, 'rtmp base')
        video_url = ncurl + clip
        thumbnail = self._search_regex(
            r"canvas:\s*\{\s*backgroundImage:\s*'url\(([^)]+)\)'", webpage,
            'thumbnail', fatal=False)

        return {
            'id': video_id,
            'title': title,
            'url': video_url,
            'ext': 'mp4',
            'is_live': True,
            'thumbnail': thumbnail,
        }
