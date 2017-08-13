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
from ..compat import compat_urllib_parse_unquote
from ..utils import url_basename


class DropboxIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?dropbox[.]com/sh?/(?P<id>[a-zA-Z0-9]{15})/.*'
    _TESTS = [
        {
            'url': 'https://www.dropbox.com/s/nelirfsxnmcfbfh/youtube-dl%20test%20video%20%27%C3%A4%22BaW_jenozKc.mp4?dl=0',
            'info_dict': {
                'id': 'nelirfsxnmcfbfh',
                'ext': 'mp4',
                'title': 'youtube-dl test video \'ä"BaW_jenozKc'
            }
        }, {
            'url': 'https://www.dropbox.com/sh/662glsejgzoj9sr/AAByil3FGH9KFNZ13e08eSa1a/Pregame%20Ceremony%20Program%20PA%2020140518.m4v',
            'only_matching': True,
        },
    ]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        fn = compat_urllib_parse_unquote(url_basename(url))
        title = os.path.splitext(fn)[0]
        video_url = re.sub(r'[?&]dl=0', '', url)
        video_url += ('?' if '?' not in video_url else '&') + 'dl=1'

        return {
            'id': video_id,
            'title': title,
            'url': video_url,
        }
