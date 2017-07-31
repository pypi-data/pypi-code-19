
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


class HentaiStigmaIE(InfoExtractor):
    _VALID_URL = r'^https?://hentai\.animestigma\.com/(?P<id>[^/]+)'
    _TEST = {
        'url': 'http://hentai.animestigma.com/inyouchuu-etsu-bonus/',
        'md5': '4e3d07422a68a4cc363d8f57c8bf0d23',
        'info_dict': {
            'id': 'inyouchuu-etsu-bonus',
            'ext': 'mp4',
            'title': 'Inyouchuu Etsu Bonus',
            'age_limit': 18,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        title = self._html_search_regex(
            r'<h2[^>]+class="posttitle"[^>]*><a[^>]*>([^<]+)</a>',
            webpage, 'title')
        wrap_url = self._html_search_regex(
            r'<iframe[^>]+src="([^"]+mp4)"', webpage, 'wrapper url')
        wrap_webpage = self._download_webpage(wrap_url, video_id)

        video_url = self._html_search_regex(
            r'file\s*:\s*"([^"]+)"', wrap_webpage, 'video url')

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'age_limit': 18,
        }
