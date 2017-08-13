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


class VShareIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?vshare\.io/[dv]/(?P<id>[^/?#&]+)'
    _TESTS = [{
        'url': 'https://vshare.io/d/0f64ce6',
        'md5': '16d7b8fef58846db47419199ff1ab3e7',
        'info_dict': {
            'id': '0f64ce6',
            'title': 'vl14062007715967',
            'ext': 'mp4',
        }
    }, {
        'url': 'https://vshare.io/v/0f64ce6/width-650/height-430/1',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(
            'https://vshare.io/d/%s' % video_id, video_id)

        title = self._html_search_regex(
            r'(?s)<div id="root-container">(.+?)<br/>', webpage, 'title')
        video_url = self._search_regex(
            r'<a[^>]+href=(["\'])(?P<url>(?:https?:)?//.+?)\1[^>]*>[Cc]lick\s+here',
            webpage, 'video url', group='url')

        return {
            'id': video_id,
            'title': title,
            'url': video_url,
        }
