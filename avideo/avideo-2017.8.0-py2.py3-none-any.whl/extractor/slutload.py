
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


class SlutloadIE(InfoExtractor):
    _VALID_URL = r'^https?://(?:\w+\.)?slutload\.com/video/[^/]+/(?P<id>[^/]+)/?$'
    _TEST = {
        'url': 'http://www.slutload.com/video/virginie-baisee-en-cam/TD73btpBqSxc/',
        'md5': '868309628ba00fd488cf516a113fd717',
        'info_dict': {
            'id': 'TD73btpBqSxc',
            'ext': 'mp4',
            'title': 'virginie baisee en cam',
            'age_limit': 18,
            'thumbnail': r're:https?://.*?\.jpg'
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        video_title = self._html_search_regex(r'<h1><strong>([^<]+)</strong>',
                                              webpage, 'title').strip()

        video_url = self._html_search_regex(
            r'(?s)<div id="vidPlayer"\s+data-url="([^"]+)"',
            webpage, 'video URL')
        thumbnail = self._html_search_regex(
            r'(?s)<div id="vidPlayer"\s+.*?previewer-file="([^"]+)"',
            webpage, 'thumbnail', fatal=False)

        return {
            'id': video_id,
            'url': video_url,
            'title': video_title,
            'thumbnail': thumbnail,
            'age_limit': 18
        }
