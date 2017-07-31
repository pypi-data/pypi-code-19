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

import base64
import re

from .common import InfoExtractor
from ..utils import parse_duration


class ChirbitIE(InfoExtractor):
    IE_NAME = 'chirbit'
    _VALID_URL = r'https?://(?:www\.)?chirb\.it/(?:(?:wp|pl)/|fb_chirbit_player\.swf\?key=)?(?P<id>[\da-zA-Z]+)'
    _TESTS = [{
        'url': 'http://chirb.it/be2abG',
        'info_dict': {
            'id': 'be2abG',
            'ext': 'mp3',
            'title': 'md5:f542ea253f5255240be4da375c6a5d7e',
            'description': 'md5:f24a4e22a71763e32da5fed59e47c770',
            'duration': 306,
            'uploader': 'Gerryaudio',
        },
        'params': {
            'skip_download': True,
        }
    }, {
        'url': 'https://chirb.it/fb_chirbit_player.swf?key=PrIPv5',
        'only_matching': True,
    }, {
        'url': 'https://chirb.it/wp/MN58c2',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        audio_id = self._match_id(url)

        webpage = self._download_webpage(
            'http://chirb.it/%s' % audio_id, audio_id)

        data_fd = self._search_regex(
            r'data-fd=(["\'])(?P<url>(?:(?!\1).)+)\1',
            webpage, 'data fd', group='url')

        # Reverse engineered from https://chirb.it/js/chirbit.player.js (look
        # for soundURL)
        audio_url = base64.b64decode(
            data_fd[::-1].encode('ascii')).decode('utf-8')

        title = self._search_regex(
            r'class=["\']chirbit-title["\'][^>]*>([^<]+)', webpage, 'title')
        description = self._search_regex(
            r'<h3>Description</h3>\s*<pre[^>]*>([^<]+)</pre>',
            webpage, 'description', default=None)
        duration = parse_duration(self._search_regex(
            r'class=["\']c-length["\'][^>]*>([^<]+)',
            webpage, 'duration', fatal=False))
        uploader = self._search_regex(
            r'id=["\']chirbit-username["\'][^>]*>([^<]+)',
            webpage, 'uploader', fatal=False)

        return {
            'id': audio_id,
            'url': audio_url,
            'title': title,
            'description': description,
            'duration': duration,
            'uploader': uploader,
        }


class ChirbitProfileIE(InfoExtractor):
    IE_NAME = 'chirbit:profile'
    _VALID_URL = r'https?://(?:www\.)?chirbit\.com/(?:rss/)?(?P<id>[^/]+)'
    _TEST = {
        'url': 'http://chirbit.com/ScarletBeauty',
        'info_dict': {
            'id': 'ScarletBeauty',
        },
        'playlist_mincount': 3,
    }

    def _real_extract(self, url):
        profile_id = self._match_id(url)

        webpage = self._download_webpage(url, profile_id)

        entries = [
            self.url_result(self._proto_relative_url('//chirb.it/' + video_id))
            for _, video_id in re.findall(r'<input[^>]+id=([\'"])copy-btn-(?P<id>[0-9a-zA-Z]+)\1', webpage)]

        return self.playlist_result(entries, profile_id)
