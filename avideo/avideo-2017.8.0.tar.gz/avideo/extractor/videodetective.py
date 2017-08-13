
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
from ..compat import compat_urlparse
from .internetvideoarchive import InternetVideoArchiveIE


class VideoDetectiveIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?videodetective\.com/[^/]+/[^/]+/(?P<id>\d+)'

    _TEST = {
        'url': 'http://www.videodetective.com/movies/kick-ass-2/194487',
        'info_dict': {
            'id': '194487',
            'ext': 'mp4',
            'title': 'KICK-ASS 2',
            'description': 'md5:c189d5b7280400630a1d3dd17eaa8d8a',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        og_video = self._og_search_video_url(webpage)
        query = compat_urlparse.urlparse(og_video).query
        return self.url_result(InternetVideoArchiveIE._build_json_url(query), ie=InternetVideoArchiveIE.ie_key())
