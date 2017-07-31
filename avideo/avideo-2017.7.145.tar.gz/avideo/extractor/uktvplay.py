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


class UKTVPlayIE(InfoExtractor):
    _VALID_URL = r'https?://uktvplay\.uktv\.co\.uk/.+?\?.*?\bvideo=(?P<id>\d+)'
    _TEST = {
        'url': 'https://uktvplay.uktv.co.uk/shows/world-at-war/c/200/watch-online/?video=2117008346001',
        'md5': '',
        'info_dict': {
            'id': '2117008346001',
            'ext': 'mp4',
            'title': 'Pincers',
            'description': 'Pincers',
            'uploader_id': '1242911124001',
            'upload_date': '20130124',
            'timestamp': 1359049267,
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'expected_warnings': ['Failed to download MPD manifest']
    }
    BRIGHTCOVE_URL_TEMPLATE = 'http://players.brightcove.net/1242911124001/H1xnMOqP_default/index.html?videoId=%s'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        return self.url_result(
            self.BRIGHTCOVE_URL_TEMPLATE % video_id,
            'BrightcoveNew', video_id)
