
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

from ..utils import str_to_int
from .keezmovies import KeezMoviesIE


class ExtremeTubeIE(KeezMoviesIE):
    _VALID_URL = r'https?://(?:www\.)?extremetube\.com/(?:[^/]+/)?video/(?P<id>[^/#?&]+)'
    _TESTS = [{
        'url': 'http://www.extremetube.com/video/music-video-14-british-euro-brit-european-cumshots-swallow-652431',
        'md5': '1fb9228f5e3332ec8c057d6ac36f33e0',
        'info_dict': {
            'id': 'music-video-14-british-euro-brit-european-cumshots-swallow-652431',
            'ext': 'mp4',
            'title': 'Music Video 14 british euro brit european cumshots swallow',
            'uploader': 'unknown',
            'view_count': int,
            'age_limit': 18,
        }
    }, {
        'url': 'http://www.extremetube.com/gay/video/abcde-1234',
        'only_matching': True,
    }, {
        'url': 'http://www.extremetube.com/video/latina-slut-fucked-by-fat-black-dick',
        'only_matching': True,
    }, {
        'url': 'http://www.extremetube.com/video/652431',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        webpage, info = self._extract_info(url)

        if not info['title']:
            info['title'] = self._search_regex(
                r'<h1[^>]+title="([^"]+)"[^>]*>', webpage, 'title')

        uploader = self._html_search_regex(
            r'Uploaded by:\s*</strong>\s*(.+?)\s*</div>',
            webpage, 'uploader', fatal=False)
        view_count = str_to_int(self._search_regex(
            r'Views:\s*</strong>\s*<span>([\d,\.]+)</span>',
            webpage, 'view count', fatal=False))

        info.update({
            'uploader': uploader,
            'view_count': view_count,
        })

        return info
