
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


class EngadgetIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?engadget\.com/video/(?P<id>[^/?#]+)'

    _TESTS = [{
        # video with 5min ID
        'url': 'http://www.engadget.com/video/518153925/',
        'md5': 'c6820d4828a5064447a4d9fc73f312c9',
        'info_dict': {
            'id': '518153925',
            'ext': 'mp4',
            'title': 'Samsung Galaxy Tab Pro 8.4 Review',
        },
        'add_ie': ['FiveMin'],
    }, {
        # video with vidible ID
        'url': 'https://www.engadget.com/video/57a28462134aa15a39f0421a/',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        return self.url_result('aol-video:%s' % video_id)
