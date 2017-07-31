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
from ..utils import url_basename


class BehindKinkIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?behindkink\.com/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<id>[^/#?_]+)'
    _TEST = {
        'url': 'http://www.behindkink.com/2014/12/05/what-are-you-passionate-about-marley-blaze/',
        'md5': '507b57d8fdcd75a41a9a7bdb7989c762',
        'info_dict': {
            'id': '37127',
            'ext': 'mp4',
            'title': 'What are you passionate about – Marley Blaze',
            'description': 'md5:aee8e9611b4ff70186f752975d9b94b4',
            'upload_date': '20141205',
            'thumbnail': 'http://www.behindkink.com/wp-content/uploads/2014/12/blaze-1.jpg',
            'age_limit': 18,
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        display_id = mobj.group('id')

        webpage = self._download_webpage(url, display_id)

        video_url = self._search_regex(
            r'<source src="([^"]+)"', webpage, 'video URL')
        video_id = url_basename(video_url).split('_')[0]
        upload_date = mobj.group('year') + mobj.group('month') + mobj.group('day')

        return {
            'id': video_id,
            'display_id': display_id,
            'url': video_url,
            'title': self._og_search_title(webpage),
            'thumbnail': self._og_search_thumbnail(webpage),
            'description': self._og_search_description(webpage),
            'upload_date': upload_date,
            'age_limit': 18,
        }
