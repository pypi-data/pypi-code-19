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


class EchoMskIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?echo\.msk\.ru/sounds/(?P<id>\d+)'
    _TEST = {
        'url': 'http://www.echo.msk.ru/sounds/1464134.html',
        'md5': '2e44b3b78daff5b458e4dbc37f191f7c',
        'info_dict': {
            'id': '1464134',
            'ext': 'mp3',
            'title': 'Особое мнение - 29 декабря 2014, 19:08',
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        audio_url = self._search_regex(
            r'<a rel="mp3" href="([^"]+)">', webpage, 'audio URL')

        title = self._html_search_regex(
            r'<a href="/programs/[^"]+" target="_blank">([^<]+)</a>',
            webpage, 'title')

        air_date = self._html_search_regex(
            r'(?s)<div class="date">(.+?)</div>',
            webpage, 'date', fatal=False, default=None)

        if air_date:
            air_date = re.sub(r'(\s)\1+', r'\1', air_date)
            if air_date:
                title = '%s - %s' % (title, air_date)

        return {
            'id': video_id,
            'url': audio_url,
            'title': title,
        }
