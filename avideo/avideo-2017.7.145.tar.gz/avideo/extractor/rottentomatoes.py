
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
from .internetvideoarchive import InternetVideoArchiveIE


class RottenTomatoesIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?rottentomatoes\.com/m/[^/]+/trailers/(?P<id>\d+)'

    _TEST = {
        'url': 'http://www.rottentomatoes.com/m/toy_story_3/trailers/11028566/',
        'info_dict': {
            'id': '11028566',
            'ext': 'mp4',
            'title': 'Toy Story 3',
            'description': 'From the creators of the beloved TOY STORY films, comes a story that will reunite the gang in a whole new way.',
            'thumbnail': r're:^https?://.*\.jpg$',
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        iva_id = self._search_regex(r'publishedid=(\d+)', webpage, 'internet video archive id')

        return {
            '_type': 'url_transparent',
            'url': 'http://video.internetvideoarchive.net/player/6/configuration.ashx?domain=www.videodetective.com&customerid=69249&playerid=641&publishedid=' + iva_id,
            'ie_key': InternetVideoArchiveIE.ie_key(),
            'id': video_id,
            'title': self._og_search_title(webpage),
        }
