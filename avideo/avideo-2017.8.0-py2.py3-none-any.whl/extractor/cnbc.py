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
from ..utils import smuggle_url


class CNBCIE(InfoExtractor):
    _VALID_URL = r'https?://video\.cnbc\.com/gallery/\?video=(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://video.cnbc.com/gallery/?video=3000503714',
        'info_dict': {
            'id': '3000503714',
            'ext': 'mp4',
            'title': 'Fighting zombies is big business',
            'description': 'md5:0c100d8e1a7947bd2feec9a5550e519e',
            'timestamp': 1459332000,
            'upload_date': '20160330',
            'uploader': 'NBCU-CNBC',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        return {
            '_type': 'url_transparent',
            'ie_key': 'ThePlatform',
            'url': smuggle_url(
                'http://link.theplatform.com/s/gZWlPC/media/guid/2408950221/%s?mbr=true&manifest=m3u' % video_id,
                {'force_smil_url': True}),
            'id': video_id,
        }
