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
    parse_duration,
    parse_iso8601,
    js_to_json,
)
from ..compat import compat_str


class RDSIE(InfoExtractor):
    IE_DESC = 'RDS.ca'
    _VALID_URL = r'https?://(?:www\.)?rds\.ca/vid(?:[eé]|%C3%A9)os/(?:[^/]+/)*(?P<id>[^/]+)-\d+\.\d+'

    _TESTS = [{
        'url': 'http://www.rds.ca/videos/football/nfl/fowler-jr-prend-la-direction-de-jacksonville-3.1132799',
        'info_dict': {
            'id': '604333',
            'display_id': 'fowler-jr-prend-la-direction-de-jacksonville',
            'ext': 'mp4',
            'title': 'Fowler Jr. prend la direction de Jacksonville',
            'description': 'Dante Fowler Jr. est le troisième choix du repêchage 2015 de la NFL. ',
            'timestamp': 1430397346,
            'upload_date': '20150430',
            'duration': 154.354,
            'age_limit': 0,
        }
    }, {
        'url': 'http://www.rds.ca/vid%C3%A9os/un-voyage-positif-3.877934',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)

        webpage = self._download_webpage(url, display_id)

        item = self._parse_json(self._search_regex(r'(?s)itemToPush\s*=\s*({.+?});', webpage, 'item'), display_id, js_to_json)
        video_id = compat_str(item['id'])
        title = item.get('title') or self._og_search_title(webpage) or self._html_search_meta(
            'title', webpage, 'title', fatal=True)
        description = self._og_search_description(webpage) or self._html_search_meta(
            'description', webpage, 'description')
        thumbnail = item.get('urlImageBig') or self._og_search_thumbnail(webpage) or self._search_regex(
            [r'<link[^>]+itemprop="thumbnailUrl"[^>]+href="([^"]+)"',
             r'<span[^>]+itemprop="thumbnailUrl"[^>]+content="([^"]+)"'],
            webpage, 'thumbnail', fatal=False)
        timestamp = parse_iso8601(self._search_regex(
            r'<span[^>]+itemprop="uploadDate"[^>]+content="([^"]+)"',
            webpage, 'upload date', fatal=False))
        duration = parse_duration(self._search_regex(
            r'<span[^>]+itemprop="duration"[^>]+content="([^"]+)"',
            webpage, 'duration', fatal=False))
        age_limit = self._family_friendly_search(webpage)

        return {
            '_type': 'url_transparent',
            'id': video_id,
            'display_id': display_id,
            'url': '9c9media:rds_web:%s' % video_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'timestamp': timestamp,
            'duration': duration,
            'age_limit': age_limit,
            'ie_key': 'NineCNineMedia',
        }
