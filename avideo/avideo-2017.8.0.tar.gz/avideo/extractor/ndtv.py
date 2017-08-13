
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
    int_or_none,
    remove_end,
    unified_strdate,
)


class NDTVIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?ndtv\.com/video/(?:[^/]+/)+[^/?^&]+-(?P<id>\d+)'

    _TEST = {
        'url': 'http://www.ndtv.com/video/news/news/ndtv-exclusive-don-t-need-character-certificate-from-rahul-gandhi-says-arvind-kejriwal-300710',
        'md5': '39f992dbe5fb531c395d8bbedb1e5e88',
        'info_dict': {
            'id': '300710',
            'ext': 'mp4',
            'title': "NDTV exclusive: Don't need character certificate from Rahul Gandhi, says Arvind Kejriwal",
            'description': 'md5:ab2d4b4a6056c5cb4caa6d729deabf02',
            'upload_date': '20131208',
            'duration': 1327,
            'thumbnail': r're:https?://.*\.jpg',
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        title = remove_end(self._og_search_title(webpage), ' - NDTV')

        filename = self._search_regex(
            r"__filename='([^']+)'", webpage, 'video filename')
        video_url = 'http://bitcast-b.bitgravity.com/ndtvod/23372/ndtv/%s' % filename

        duration = int_or_none(self._search_regex(
            r"__duration='([^']+)'", webpage, 'duration', fatal=False))

        upload_date = unified_strdate(self._html_search_meta(
            'publish-date', webpage, 'upload date', fatal=False))

        description = remove_end(self._og_search_description(webpage), ' (Read more)')

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'description': description,
            'thumbnail': self._og_search_thumbnail(webpage),
            'duration': duration,
            'upload_date': upload_date,
        }
