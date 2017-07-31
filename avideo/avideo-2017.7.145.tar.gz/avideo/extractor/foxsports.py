
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
from ..utils import (
    smuggle_url,
    update_url_query,
)


class FoxSportsIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?foxsports\.com/(?:[^/]+/)*(?P<id>[^/]+)'

    _TEST = {
        'url': 'http://www.foxsports.com/tennessee/video/432609859715',
        'md5': 'b49050e955bebe32c301972e4012ac17',
        'info_dict': {
            'id': 'bwduI3X_TgUB',
            'ext': 'mp4',
            'title': 'Courtney Lee on going up 2-0 in series vs. Blazers',
            'description': 'Courtney Lee talks about Memphis being focused.',
            'upload_date': '20150423',
            'timestamp': 1429761109,
            'uploader': 'NEWA-FNG-FOXSPORTS',
        },
        'add_ie': ['ThePlatform'],
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        config = self._parse_json(
            self._html_search_regex(
                r"""class="[^"]*(?:fs-player|platformPlayer-wrapper)[^"]*".+?data-player-config='([^']+)'""",
                webpage, 'data player config'),
            video_id)

        return self.url_result(smuggle_url(update_url_query(
            config['releaseURL'], {
                'mbr': 'true',
                'switch': 'http',
            }), {'force_smil_url': True}))
