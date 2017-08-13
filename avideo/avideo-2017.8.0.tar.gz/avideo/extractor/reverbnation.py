
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
    qualities,
    str_or_none,
)


class ReverbNationIE(InfoExtractor):
    _VALID_URL = r'^https?://(?:www\.)?reverbnation\.com/.*?/song/(?P<id>\d+).*?$'
    _TESTS = [{
        'url': 'http://www.reverbnation.com/alkilados/song/16965047-mona-lisa',
        'md5': 'c0aaf339bcee189495fdf5a8c8ba8645',
        'info_dict': {
            'id': '16965047',
            'ext': 'mp3',
            'title': 'MONA LISA',
            'uploader': 'ALKILADOS',
            'uploader_id': '216429',
            'thumbnail': r're:^https?://.*\.jpg',
        },
    }]

    def _real_extract(self, url):
        song_id = self._match_id(url)

        api_res = self._download_json(
            'https://api.reverbnation.com/song/%s' % song_id,
            song_id,
            note='Downloading information of song %s' % song_id
        )

        THUMBNAILS = ('thumbnail', 'image')
        quality = qualities(THUMBNAILS)
        thumbnails = []
        for thumb_key in THUMBNAILS:
            if api_res.get(thumb_key):
                thumbnails.append({
                    'url': api_res[thumb_key],
                    'preference': quality(thumb_key)
                })

        return {
            'id': song_id,
            'title': api_res['name'],
            'url': api_res['url'],
            'uploader': api_res.get('artist', {}).get('name'),
            'uploader_id': str_or_none(api_res.get('artist', {}).get('id')),
            'thumbnails': thumbnails,
            'ext': 'mp3',
            'vcodec': 'none',
        }
