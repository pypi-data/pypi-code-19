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

from .vice import ViceBaseIE


class VicelandIE(ViceBaseIE):
    _VALID_URL = r'https?://(?:www\.)?viceland\.com/(?P<locale>[^/]+)/video/[^/]+/(?P<id>[a-f0-9]+)'
    _TEST = {
        'url': 'https://www.viceland.com/en_us/video/trapped/588a70d0dba8a16007de7316',
        'info_dict': {
            'id': '588a70d0dba8a16007de7316',
            'ext': 'mp4',
            'title': 'TRAPPED (Series Trailer)',
            'description': 'md5:7a8e95c2b6cd86461502a2845e581ccf',
            'age_limit': 14,
            'timestamp': 1485474122,
            'upload_date': '20170126',
            'uploader_id': '57a204098cb727dec794c6a3',
            'uploader': 'Viceland',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'add_ie': ['UplynkPreplay'],
        'skip': '404',
    }
    _PREPLAY_HOST = 'www.viceland'

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        locale = mobj.group('locale')
        webpage = self._download_webpage(url, video_id)
        return self._extract_preplay_video(url, locale, webpage)
