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
from ..utils import urljoin


class YourUploadIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?(?:yourupload\.com/(?:watch|embed)|embed\.yourupload\.com)/(?P<id>[A-Za-z0-9]+)'
    _TESTS = [{
        'url': 'http://yourupload.com/watch/14i14h',
        'md5': '5e2c63385454c557f97c4c4131a393cd',
        'info_dict': {
            'id': '14i14h',
            'ext': 'mp4',
            'title': 'BigBuckBunny_320x180.mp4',
            'thumbnail': r're:^https?://.*\.jpe?g',
        }
    }, {
        'url': 'http://www.yourupload.com/embed/14i14h',
        'only_matching': True,
    }, {
        'url': 'http://embed.yourupload.com/14i14h',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        embed_url = 'http://www.yourupload.com/embed/%s' % video_id

        webpage = self._download_webpage(embed_url, video_id)

        title = self._og_search_title(webpage)
        video_url = urljoin(embed_url, self._og_search_video_url(webpage))
        thumbnail = self._og_search_thumbnail(webpage, default=None)

        return {
            'id': video_id,
            'title': title,
            'url': video_url,
            'thumbnail': thumbnail,
            'http_headers': {
                'Referer': embed_url,
            },
        }
