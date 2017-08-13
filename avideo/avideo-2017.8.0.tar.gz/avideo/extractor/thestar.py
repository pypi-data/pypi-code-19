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


class TheStarIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?thestar\.com/(?:[^/]+/)*(?P<id>.+)\.html'
    _TEST = {
        'url': 'http://www.thestar.com/life/2016/02/01/mankind-why-this-woman-started-a-men-s-skincare-line.html',
        'md5': '2c62dd4db2027e35579fefb97a8b6554',
        'info_dict': {
            'id': '4732393888001',
            'ext': 'mp4',
            'title': 'Mankind: Why this woman started a men\'s skin care line',
            'description': 'Robert Cribb talks to Young Lee, the founder of Uncle Peter\'s MAN.',
            'uploader_id': '794267642001',
            'timestamp': 1454353482,
            'upload_date': '20160201',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        }
    }
    BRIGHTCOVE_URL_TEMPLATE = 'http://players.brightcove.net/794267642001/default_default/index.html?videoId=%s'

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        brightcove_id = self._search_regex(
            r'mainartBrightcoveVideoId["\']?\s*:\s*["\']?(\d+)',
            webpage, 'brightcove id')
        return self.url_result(
            self.BRIGHTCOVE_URL_TEMPLATE % brightcove_id,
            'BrightcoveNew', brightcove_id)
