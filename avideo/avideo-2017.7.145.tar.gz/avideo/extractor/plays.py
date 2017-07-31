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
from ..utils import int_or_none


class PlaysTVIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?plays\.tv/(?:video|embeds)/(?P<id>[0-9a-f]{18})'
    _TESTS = [{
        'url': 'https://plays.tv/video/56af17f56c95335490/when-you-outplay-the-azir-wall',
        'md5': 'dfeac1198506652b5257a62762cec7bc',
        'info_dict': {
            'id': '56af17f56c95335490',
            'ext': 'mp4',
            'title': 'Bjergsen - When you outplay the Azir wall',
            'description': 'Posted by Bjergsen',
        }
    }, {
        'url': 'https://plays.tv/embeds/56af17f56c95335490',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(
            'https://plays.tv/video/%s' % video_id, video_id)

        info = self._search_json_ld(webpage, video_id,)

        mpd_url, sources = re.search(
            r'(?s)<video[^>]+data-mpd="([^"]+)"[^>]*>(.+?)</video>',
            webpage).groups()
        formats = self._extract_mpd_formats(
            self._proto_relative_url(mpd_url), video_id, mpd_id='DASH')
        for format_id, height, format_url in re.findall(r'<source\s+res="((\d+)h?)"\s+src="([^"]+)"', sources):
            formats.append({
                'url': self._proto_relative_url(format_url),
                'format_id': 'http-' + format_id,
                'height': int_or_none(height),
            })
        self._sort_formats(formats)

        info.update({
            'id': video_id,
            'description': self._og_search_description(webpage),
            'thumbnail': info.get('thumbnail') or self._og_search_thumbnail(webpage),
            'formats': formats,
        })

        return info
