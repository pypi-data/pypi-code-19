
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


class Ku6IE(InfoExtractor):
    _VALID_URL = r'https?://v\.ku6\.com/show/(?P<id>[a-zA-Z0-9\-\_]+)(?:\.)*html'
    _TEST = {
        'url': 'http://v.ku6.com/show/JG-8yS14xzBr4bCn1pu0xw...html',
        'md5': '01203549b9efbb45f4b87d55bdea1ed1',
        'info_dict': {
            'id': 'JG-8yS14xzBr4bCn1pu0xw',
            'ext': 'f4v',
            'title': 'techniques test',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        title = self._html_search_regex(
            r'<h1 title=.*>(.*?)</h1>', webpage, 'title')
        dataUrl = 'http://v.ku6.com/fetchVideo4Player/%s.html' % video_id
        jsonData = self._download_json(dataUrl, video_id)
        downloadUrl = jsonData['data']['f']

        return {
            'id': video_id,
            'title': title,
            'url': downloadUrl
        }
