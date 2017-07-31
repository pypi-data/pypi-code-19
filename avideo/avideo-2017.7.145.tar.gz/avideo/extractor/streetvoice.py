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
from ..compat import compat_str
from ..utils import unified_strdate


class StreetVoiceIE(InfoExtractor):
    _VALID_URL = r'https?://(?:.+?\.)?streetvoice\.com/[^/]+/songs/(?P<id>[0-9]+)'
    _TESTS = [{
        'url': 'http://streetvoice.com/skippylu/songs/94440/',
        'md5': '15974627fc01a29e492c98593c2fd472',
        'info_dict': {
            'id': '94440',
            'ext': 'mp3',
            'title': '輸',
            'description': 'Crispy脆樂團 - 輸',
            'thumbnail': r're:^https?://.*\.jpg$',
            'duration': 260,
            'upload_date': '20091018',
            'uploader': 'Crispy脆樂團',
            'uploader_id': '627810',
        }
    }, {
        'url': 'http://tw.streetvoice.com/skippylu/songs/94440/',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        song_id = self._match_id(url)

        song = self._download_json(
            'https://streetvoice.com/api/v1/public/song/%s/' % song_id, song_id, data=b'')

        title = song['name']
        author = song['user']['nickname']

        return {
            'id': song_id,
            'url': song['file'],
            'title': title,
            'description': '%s - %s' % (author, title),
            'thumbnail': self._proto_relative_url(song.get('image'), 'http:'),
            'duration': song.get('length'),
            'upload_date': unified_strdate(song.get('created_at')),
            'uploader': author,
            'uploader_id': compat_str(song['user']['id']),
        }
