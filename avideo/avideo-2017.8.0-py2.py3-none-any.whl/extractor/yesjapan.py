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
    HEADRequest,
    get_element_by_attribute,
    parse_iso8601,
)


class YesJapanIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?yesjapan\.com/video/(?P<slug>[A-Za-z0-9\-]*)_(?P<id>[A-Za-z0-9]+)\.html'
    _TEST = {
        'url': 'http://www.yesjapan.com/video/japanese-in-5-20-wa-and-ga-particle-usages_726497834.html',
        'md5': 'f0be416314e5be21a12b499b330c21cf',
        'info_dict': {
            'id': '726497834',
            'title': 'Japanese in 5! #20 - WA And GA Particle Usages',
            'description': 'This should clear up some issues most students of Japanese encounter with WA and GA....',
            'ext': 'mp4',
            'timestamp': 1416391590,
            'upload_date': '20141119',
            'thumbnail': r're:^https?://.*\.jpg$',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)
        title = self._og_search_title(webpage)
        video_url = self._og_search_video_url(webpage)
        description = self._og_search_description(webpage)
        thumbnail = self._og_search_thumbnail(webpage)

        timestamp = None
        submit_info = get_element_by_attribute('class', 'pm-submit-data', webpage)
        if submit_info:
            timestamp = parse_iso8601(self._search_regex(
                r'datetime="([^"]+)"', submit_info, 'upload date', fatal=False, default=None))

        # attempt to resolve the final URL in order to get a proper extension
        redirect_req = HEADRequest(video_url)
        req = self._request_webpage(
            redirect_req, video_id, note='Resolving final URL', errnote='Could not resolve final URL', fatal=False)
        if req:
            video_url = req.geturl()

        formats = [{
            'format_id': 'sd',
            'url': video_url,
        }]

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
            'description': description,
            'timestamp': timestamp,
            'thumbnail': thumbnail,
        }
