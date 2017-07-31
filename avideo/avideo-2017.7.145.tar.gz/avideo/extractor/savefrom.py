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

import os.path
import re

from .common import InfoExtractor


class SaveFromIE(InfoExtractor):
    IE_NAME = 'savefrom.net'
    _VALID_URL = r'https?://[^.]+\.savefrom\.net/\#url=(?P<url>.*)$'

    _TEST = {
        'url': 'http://en.savefrom.net/#url=http://youtube.com/watch?v=UlVRAPW2WJY&utm_source=youtube.com&utm_medium=short_domains&utm_campaign=ssyoutube.com',
        'info_dict': {
            'id': 'UlVRAPW2WJY',
            'ext': 'mp4',
            'title': 'About Team Radical MMA | MMA Fighting',
            'upload_date': '20120816',
            'uploader': 'Howcast',
            'uploader_id': 'Howcast',
            'description': r're:(?s).* Hi, my name is Rene Dreifuss\. And I\'m here to show you some MMA.*',
        },
        'params': {
            'skip_download': True
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = os.path.splitext(url.split('/')[-1])[0]
        return {
            '_type': 'url',
            'id': video_id,
            'url': mobj.group('url'),
        }
