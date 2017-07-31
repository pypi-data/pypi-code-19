
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
import random

from .common import InfoExtractor


class VideoPremiumIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?videopremium\.(?:tv|me)/(?P<id>\w+)(?:/.*)?'
    _TEST = {
        'url': 'http://videopremium.tv/4w7oadjsf156',
        'info_dict': {
            'id': '4w7oadjsf156',
            'ext': 'f4v',
            'title': 'youtube-dl_test_video____a_________-BaW_jenozKc.mp4.mp4'
        },
        'params': {
            'skip_download': True,
        },
        'skip': 'Test file has been deleted.',
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage_url = 'http://videopremium.tv/' + video_id
        webpage = self._download_webpage(webpage_url, video_id)

        if re.match(r'^<html><head><script[^>]*>window.location\s*=', webpage):
            # Download again, we need a cookie
            webpage = self._download_webpage(
                webpage_url, video_id,
                note='Downloading webpage again (with cookie)')

        video_title = self._html_search_regex(
            r'<h2(?:.*?)>\s*(.+?)\s*<', webpage, 'video title')

        return {
            'id': video_id,
            'url': 'rtmp://e%d.md.iplay.md/play' % random.randint(1, 16),
            'play_path': 'mp4:%s.f4v' % video_id,
            'page_url': 'http://videopremium.tv/' + video_id,
            'player_url': 'http://videopremium.tv/uplayer/uppod.swf',
            'ext': 'f4v',
            'title': video_title,
        }
