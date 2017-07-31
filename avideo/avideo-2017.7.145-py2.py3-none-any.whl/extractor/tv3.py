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


class TV3IE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?tv3\.co\.nz/(?P<id>[^/]+)/tabid/\d+/articleID/\d+/MCat/\d+/Default\.aspx'
    _TEST = {
        'url': 'http://www.tv3.co.nz/MOTORSPORT-SRS-SsangYong-Hampton-Downs-Round-3/tabid/3692/articleID/121615/MCat/2915/Default.aspx',
        'info_dict': {
            'id': '4659127992001',
            'ext': 'mp4',
            'title': 'CRC Motorsport: SRS SsangYong Hampton Downs Round 3 - S2015 Ep3',
            'description': 'SsangYong Racing Series returns for Round 3 with drivers from New Zealand and Australia taking to the grid at Hampton Downs raceway.',
            'uploader_id': '3812193411001',
            'upload_date': '20151213',
            'timestamp': 1449975272,
        },
        'expected_warnings': [
            'Failed to download MPD manifest'
        ],
        'params': {
            # m3u8 download
            'skip_download': True,
        },
    }
    BRIGHTCOVE_URL_TEMPLATE = 'http://players.brightcove.net/3812193411001/default_default/index.html?videoId=%s'

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        brightcove_id = self._search_regex(r'<param\s*name="@videoPlayer"\s*value="(\d+)"', webpage, 'brightcove id')
        return self.url_result(self.BRIGHTCOVE_URL_TEMPLATE % brightcove_id, 'BrightcoveNew', brightcove_id)
