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
    qualities,
    unified_timestamp,
)


class PearVideoIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?pearvideo\.com/video_(?P<id>\d+)'
    _TEST = {
        'url': 'http://www.pearvideo.com/video_1076290',
        'info_dict': {
            'id': '1076290',
            'ext': 'mp4',
            'title': '小浣熊在主人家玻璃上滚石头：没砸',
            'description': 'md5:01d576b747de71be0ee85eb7cac25f9d',
            'timestamp': 1494275280,
            'upload_date': '20170508',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        quality = qualities(
            ('ldflv', 'ld', 'sdflv', 'sd', 'hdflv', 'hd', 'src'))

        formats = [{
            'url': mobj.group('url'),
            'format_id': mobj.group('id'),
            'quality': quality(mobj.group('id')),
        } for mobj in re.finditer(
            r'(?P<id>[a-zA-Z]+)Url\s*=\s*(["\'])(?P<url>(?:https?:)?//.+?)\2',
            webpage)]
        self._sort_formats(formats)

        title = self._search_regex(
            (r'<h1[^>]+\bclass=(["\'])video-tt\1[^>]*>(?P<value>[^<]+)',
             r'<[^>]+\bdata-title=(["\'])(?P<value>(?:(?!\1).)+)\1'),
            webpage, 'title', group='value')
        description = self._search_regex(
            (r'<div[^>]+\bclass=(["\'])summary\1[^>]*>(?P<value>[^<]+)',
             r'<[^>]+\bdata-summary=(["\'])(?P<value>(?:(?!\1).)+)\1'),
            webpage, 'description', default=None,
            group='value') or self._html_search_meta('Description', webpage)
        timestamp = unified_timestamp(self._search_regex(
            r'<div[^>]+\bclass=["\']date["\'][^>]*>([^<]+)',
            webpage, 'timestamp', fatal=False))

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'timestamp': timestamp,
            'formats': formats,
        }
