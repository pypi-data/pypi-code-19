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


class MoviezineIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?moviezine\.se/video/(?P<id>[^?#]+)'

    _TEST = {
        'url': 'http://www.moviezine.se/video/205866',
        'info_dict': {
            'id': '205866',
            'ext': 'mp4',
            'title': 'Oculus - Trailer 1',
            'description': 'md5:40cc6790fc81d931850ca9249b40e8a4',
            'thumbnail': r're:http://.*\.jpg',
        },
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')

        webpage = self._download_webpage(url, video_id)
        jsplayer = self._download_webpage('http://www.moviezine.se/api/player.js?video=%s' % video_id, video_id, 'Downloading js api player')

        formats = [{
            'format_id': 'sd',
            'url': self._html_search_regex(r'file: "(.+?)",', jsplayer, 'file'),
            'quality': 0,
            'ext': 'mp4',
        }]

        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': self._search_regex(r'title: "(.+?)",', jsplayer, 'title'),
            'thumbnail': self._search_regex(r'image: "(.+?)",', jsplayer, 'image'),
            'formats': formats,
            'description': self._og_search_description(webpage),
        }
