
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

from ..compat import compat_urlparse


class TheSceneIE(InfoExtractor):
    _VALID_URL = r'https?://thescene\.com/watch/[^/]+/(?P<id>[^/#?]+)'

    _TEST = {
        'url': 'https://thescene.com/watch/vogue/narciso-rodriguez-spring-2013-ready-to-wear',
        'info_dict': {
            'id': '520e8faac2b4c00e3c6e5f43',
            'ext': 'mp4',
            'title': 'Narciso Rodriguez: Spring 2013 Ready-to-Wear',
            'display_id': 'narciso-rodriguez-spring-2013-ready-to-wear',
            'duration': 127,
            'series': 'Style.com Fashion Shows',
            'season': 'Ready To Wear Spring 2013',
            'tags': list,
            'categories': list,
            'upload_date': '20120913',
            'timestamp': 1347512400,
            'uploader': 'vogue',
        },
    }

    def _real_extract(self, url):
        display_id = self._match_id(url)

        webpage = self._download_webpage(url, display_id)

        player_url = compat_urlparse.urljoin(
            url,
            self._html_search_regex(
                r'id=\'js-player-script\'[^>]+src=\'(.+?)\'', webpage, 'player url'))

        return {
            '_type': 'url_transparent',
            'display_id': display_id,
            'url': player_url,
            'ie_key': 'CondeNast',
        }
