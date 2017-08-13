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


class SonyLIVIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?sonyliv\.com/details/[^/]+/(?P<id>\d+)'
    _TESTS = [{
        'url': "http://www.sonyliv.com/details/episodes/5024612095001/Ep.-1---Achaari-Cheese-Toast---Bachelor's-Delight",
        'info_dict': {
            'title': "Ep. 1 - Achaari Cheese Toast - Bachelor's Delight",
            'id': '5024612095001',
            'ext': 'mp4',
            'upload_date': '20160707',
            'description': 'md5:7f28509a148d5be9d0782b4d5106410d',
            'uploader_id': '4338955589001',
            'timestamp': 1467870968,
        },
        'params': {
            'skip_download': True,
        },
        'add_ie': ['BrightcoveNew'],
    }, {
        'url': 'http://www.sonyliv.com/details/full%20movie/4951168986001/Sei-Raat-(Bangla)',
        'only_matching': True,
    }]

    BRIGHTCOVE_URL_TEMPLATE = 'http://players.brightcove.net/4338955589001/default_default/index.html?videoId=%s'

    def _real_extract(self, url):
        brightcove_id = self._match_id(url)
        return self.url_result(
            self.BRIGHTCOVE_URL_TEMPLATE % brightcove_id, 'BrightcoveNew', brightcove_id)
