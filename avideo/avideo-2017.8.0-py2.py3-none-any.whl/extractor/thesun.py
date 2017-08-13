
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

import re

from .common import InfoExtractor
from .ooyala import OoyalaIE


class TheSunIE(InfoExtractor):
    _VALID_URL = r'https://(?:www\.)?thesun\.co\.uk/[^/]+/(?P<id>\d+)'
    _TEST = {
        'url': 'https://www.thesun.co.uk/tvandshowbiz/2261604/orlando-bloom-and-katy-perry-post-adorable-instagram-video-together-celebrating-thanksgiving-after-split-rumours/',
        'info_dict': {
            'id': '2261604',
            'title': 'md5:cba22f48bad9218b64d5bbe0e16afddf',
        },
        'playlist_count': 2,
    }

    def _real_extract(self, url):
        article_id = self._match_id(url)

        webpage = self._download_webpage(url, article_id)

        entries = []
        for ooyala_id in re.findall(
                r'<[^>]+\b(?:id\s*=\s*"thesun-ooyala-player-|data-content-id\s*=\s*")([^"]+)',
                webpage):
            entries.append(OoyalaIE._build_url_result(ooyala_id))

        return self.playlist_result(
            entries, article_id, self._og_search_title(webpage, fatal=False))
