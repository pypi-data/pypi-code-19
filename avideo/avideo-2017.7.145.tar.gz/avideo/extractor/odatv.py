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

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    NO_DEFAULT,
    remove_start
)


class OdaTVIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?odatv\.com/(?:mob|vid)_video\.php\?.*\bid=(?P<id>[^&]+)'
    _TESTS = [{
        'url': 'http://odatv.com/vid_video.php?id=8E388',
        'md5': 'dc61d052f205c9bf2da3545691485154',
        'info_dict': {
            'id': '8E388',
            'ext': 'mp4',
            'title': 'Artık Davutoğlu ile devam edemeyiz'
        }
    }, {
        # mobile URL
        'url': 'http://odatv.com/mob_video.php?id=8E388',
        'only_matching': True,
    }, {
        # no video
        'url': 'http://odatv.com/mob_video.php?id=8E900',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        no_video = 'NO VIDEO!' in webpage

        video_url = self._search_regex(
            r'mp4\s*:\s*(["\'])(?P<url>http.+?)\1', webpage, 'video url',
            default=None if no_video else NO_DEFAULT, group='url')

        if no_video:
            raise ExtractorError('Video %s does not exist' % video_id, expected=True)

        return {
            'id': video_id,
            'url': video_url,
            'title': remove_start(self._og_search_title(webpage), 'Video: '),
            'thumbnail': self._og_search_thumbnail(webpage),
        }
