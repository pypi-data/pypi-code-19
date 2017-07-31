
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
from ..utils import ExtractorError


class MacGameStoreIE(InfoExtractor):
    IE_NAME = 'macgamestore'
    IE_DESC = 'MacGameStore trailers'
    _VALID_URL = r'https?://(?:www\.)?macgamestore\.com/mediaviewer\.php\?trailer=(?P<id>\d+)'

    _TEST = {
        'url': 'http://www.macgamestore.com/mediaviewer.php?trailer=2450',
        'md5': '8649b8ea684b6666b4c5be736ecddc61',
        'info_dict': {
            'id': '2450',
            'ext': 'm4v',
            'title': 'Crow',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(
            url, video_id, 'Downloading trailer page')

        if '>Missing Media<' in webpage:
            raise ExtractorError(
                'Trailer %s does not exist' % video_id, expected=True)

        video_title = self._html_search_regex(
            r'<title>MacGameStore: (.*?) Trailer</title>', webpage, 'title')

        video_url = self._html_search_regex(
            r'(?s)<div\s+id="video-player".*?href="([^"]+)"\s*>',
            webpage, 'video URL')

        return {
            'id': video_id,
            'url': video_url,
            'title': video_title
        }
