
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


class AlJazeeraIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?aljazeera\.com/(?:programmes|video)/.*?/(?P<id>[^/]+)\.html'

    _TESTS = [{
        'url': 'http://www.aljazeera.com/programmes/the-slum/2014/08/deliverance-201482883754237240.html',
        'info_dict': {
            'id': '3792260579001',
            'ext': 'mp4',
            'title': 'The Slum - Episode 1: Deliverance',
            'description': 'As a birth attendant advocating for family planning, Remy is on the frontline of Tondo\'s battle with overcrowding.',
            'uploader_id': '665003303001',
            'timestamp': 1411116829,
            'upload_date': '20140919',
        },
        'add_ie': ['BrightcoveNew'],
        'skip': 'Not accessible from Travis CI server',
    }, {
        'url': 'http://www.aljazeera.com/video/news/2017/05/sierra-leone-709-carat-diamond-auctioned-170511100111930.html',
        'only_matching': True,
    }]
    BRIGHTCOVE_URL_TEMPLATE = 'http://players.brightcove.net/665003303001/default_default/index.html?videoId=%s'

    def _real_extract(self, url):
        program_name = self._match_id(url)
        webpage = self._download_webpage(url, program_name)
        brightcove_id = self._search_regex(
            r'RenderPagesVideo\(\'(.+?)\'', webpage, 'brightcove id')
        return self.url_result(self.BRIGHTCOVE_URL_TEMPLATE % brightcove_id, 'BrightcoveNew', brightcove_id)
