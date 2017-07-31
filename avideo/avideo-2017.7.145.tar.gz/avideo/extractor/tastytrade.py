
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
from .ooyala import OoyalaIE


class TastyTradeIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?tastytrade\.com/tt/shows/[^/]+/episodes/(?P<id>[^/?#&]+)'

    _TESTS = [{
        'url': 'https://www.tastytrade.com/tt/shows/market-measures/episodes/correlation-in-short-volatility-06-28-2017',
        'info_dict': {
            'id': 'F3bnlzbToeI6pLEfRyrlfooIILUjz4nM',
            'ext': 'mp4',
            'title': 'A History of Teaming',
            'description': 'md5:2a9033db8da81f2edffa4c99888140b3',
            'duration': 422.255,
        },
        'params': {
            'skip_download': True,
        },
        'add_ie': ['Ooyala'],
    }, {
        'url': 'https://www.tastytrade.com/tt/shows/daily-dose/episodes/daily-dose-06-30-2017',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        ooyala_code = self._search_regex(
            r'data-media-id=(["\'])(?P<code>(?:(?!\1).)+)\1',
            webpage, 'ooyala code', group='code')

        info = self._search_json_ld(webpage, display_id, fatal=False)
        info.update({
            '_type': 'url_transparent',
            'ie_key': OoyalaIE.ie_key(),
            'url': 'ooyala:%s' % ooyala_code,
            'display_id': display_id,
        })
        return info
