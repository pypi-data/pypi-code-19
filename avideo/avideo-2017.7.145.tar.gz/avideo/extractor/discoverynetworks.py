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

import re

from .common import InfoExtractor
from .brightcove import BrightcoveLegacyIE
from ..compat import (
    compat_parse_qs,
    compat_urlparse,
)
from ..utils import smuggle_url


class DiscoveryNetworksDeIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?(?:discovery|tlc|animalplanet|dmax)\.de/(?:.*#(?P<id>\d+)|(?:[^/]+/)*videos/(?P<title>[^/?#]+))'

    _TESTS = [{
        'url': 'http://www.tlc.de/sendungen/breaking-amish/videos/#3235167922001',
        'info_dict': {
            'id': '3235167922001',
            'ext': 'mp4',
            'title': 'Breaking Amish: Die Welt da draußen',
            'description': (
                'Vier Amische und eine Mennonitin wagen in New York'
                '  den Sprung in ein komplett anderes Leben. Begleitet sie auf'
                ' ihrem spannenden Weg.'),
            'timestamp': 1396598084,
            'upload_date': '20140404',
            'uploader_id': '1659832546',
        },
    }, {
        'url': 'http://www.dmax.de/programme/storage-hunters-uk/videos/storage-hunters-uk-episode-6/',
        'only_matching': True,
    }, {
        'url': 'http://www.discovery.de/#5332316765001',
        'only_matching': True,
    }]
    BRIGHTCOVE_URL_TEMPLATE = 'http://players.brightcove.net/1659832546/default_default/index.html?videoId=%s'

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        brightcove_id = mobj.group('id')
        if not brightcove_id:
            title = mobj.group('title')
            webpage = self._download_webpage(url, title)
            brightcove_legacy_url = BrightcoveLegacyIE._extract_brightcove_url(webpage)
            brightcove_id = compat_parse_qs(compat_urlparse.urlparse(
                brightcove_legacy_url).query)['@videoPlayer'][0]
        return self.url_result(smuggle_url(
            self.BRIGHTCOVE_URL_TEMPLATE % brightcove_id, {'geo_countries': ['DE']}),
            'BrightcoveNew', brightcove_id)
