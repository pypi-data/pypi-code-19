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


class LCIIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?lci\.fr/[^/]+/[\w-]+-(?P<id>\d+)\.html'
    _TEST = {
        'url': 'http://www.lci.fr/international/etats-unis-a-j-62-hillary-clinton-reste-sans-voix-2001679.html',
        'md5': '2fdb2538b884d4d695f9bd2bde137e6c',
        'info_dict': {
            'id': '13244802',
            'ext': 'mp4',
            'title': 'Hillary Clinton et sa quinte de toux, en plein meeting',
            'description': 'md5:a4363e3a960860132f8124b62f4a01c9',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        wat_id = self._search_regex(r'data-watid=[\'"](\d+)', webpage, 'wat id')
        return self.url_result('wat:' + wat_id, 'Wat', wat_id)
