
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


class EbaumsWorldIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?ebaumsworld\.com/videos/[^/]+/(?P<id>\d+)'

    _TEST = {
        'url': 'http://www.ebaumsworld.com/videos/a-giant-python-opens-the-door/83367677/',
        'info_dict': {
            'id': '83367677',
            'ext': 'mp4',
            'title': 'A Giant Python Opens The Door',
            'description': 'This is how nightmares start...',
            'uploader': 'jihadpizza',
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        config = self._download_xml(
            'http://www.ebaumsworld.com/video/player/%s' % video_id, video_id)
        video_url = config.find('file').text

        return {
            'id': video_id,
            'title': config.find('title').text,
            'url': video_url,
            'description': config.find('description').text,
            'thumbnail': config.find('image').text,
            'uploader': config.find('username').text,
        }
