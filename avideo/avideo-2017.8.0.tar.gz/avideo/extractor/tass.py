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

import json

from .common import InfoExtractor
from ..utils import (
    js_to_json,
    qualities,
)


class TassIE(InfoExtractor):
    _VALID_URL = r'https?://(?:tass\.ru|itar-tass\.com)/[^/]+/(?P<id>\d+)'
    _TESTS = [
        {
            'url': 'http://tass.ru/obschestvo/1586870',
            'md5': '3b4cdd011bc59174596b6145cda474a4',
            'info_dict': {
                'id': '1586870',
                'ext': 'mp4',
                'title': 'Посетителям московского зоопарка показали красную панду',
                'description': 'Приехавшую из Дублина Зейну можно увидеть в павильоне "Кошки тропиков"',
                'thumbnail': r're:^https?://.*\.jpg$',
            },
        },
        {
            'url': 'http://itar-tass.com/obschestvo/1600009',
            'only_matching': True,
        },
    ]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        sources = json.loads(js_to_json(self._search_regex(
            r'(?s)sources\s*:\s*(\[.+?\])', webpage, 'sources')))

        quality = qualities(['sd', 'hd'])

        formats = []
        for source in sources:
            video_url = source.get('file')
            if not video_url or not video_url.startswith('http') or not video_url.endswith('.mp4'):
                continue
            label = source.get('label')
            formats.append({
                'url': video_url,
                'format_id': label,
                'quality': quality(label),
            })
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': self._og_search_title(webpage),
            'description': self._og_search_description(webpage),
            'thumbnail': self._og_search_thumbnail(webpage),
            'formats': formats,
        }
