
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
from ..utils import unified_strdate, determine_ext


class RoxwelIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?roxwel\.com/player/(?P<filename>.+?)(\.|\?|$)'

    _TEST = {
        'url': 'http://www.roxwel.com/player/passionpittakeawalklive.html',
        'info_dict': {
            'id': 'passionpittakeawalklive',
            'ext': 'flv',
            'title': 'Take A Walk (live)',
            'uploader': 'Passion Pit',
            'uploader_id': 'passionpit',
            'upload_date': '20120928',
            'description': 'Passion Pit performs "Take A Walk\" live at The Backyard in Austin, Texas. ',
        },
        'params': {
            # rtmp download
            'skip_download': True,
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        filename = mobj.group('filename')
        info_url = 'http://www.roxwel.com/api/videos/%s' % filename
        info = self._download_json(info_url, filename)

        rtmp_rates = sorted([int(r.replace('flv_', '')) for r in info['media_rates'] if r.startswith('flv_')])
        best_rate = rtmp_rates[-1]
        url_page_url = 'http://roxwel.com/pl_one_time.php?filename=%s&quality=%s' % (filename, best_rate)
        rtmp_url = self._download_webpage(url_page_url, filename, 'Downloading video url')
        ext = determine_ext(rtmp_url)
        if ext == 'f4v':
            rtmp_url = rtmp_url.replace(filename, 'mp4:%s' % filename)

        return {
            'id': filename,
            'title': info['title'],
            'url': rtmp_url,
            'ext': 'flv',
            'description': info['description'],
            'thumbnail': info.get('player_image_url') or info.get('image_url_large'),
            'uploader': info['artist'],
            'uploader_id': info['artistname'],
            'upload_date': unified_strdate(info['dbdate']),
        }
