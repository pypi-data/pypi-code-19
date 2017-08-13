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
from ..utils import (
    ExtractorError,
    int_or_none,
    sanitized_Request,
    urlencode_postdata,
)


class TubiTvIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?tubitv\.com/video/(?P<id>[0-9]+)'
    _LOGIN_URL = 'http://tubitv.com/login'
    _NETRC_MACHINE = 'tubitv'
    _GEO_COUNTRIES = ['US']
    _TEST = {
        'url': 'http://tubitv.com/video/283829/the_comedian_at_the_friday',
        'md5': '43ac06be9326f41912dc64ccf7a80320',
        'info_dict': {
            'id': '283829',
            'ext': 'mp4',
            'title': 'The Comedian at The Friday',
            'description': 'A stand up comedian is forced to look at the decisions in his life while on a one week trip to the west coast.',
            'uploader_id': 'bc168bee0d18dd1cb3b86c68706ab434',
        },
    }

    def _login(self):
        (username, password) = self._get_login_info()
        if username is None:
            return
        self.report_login()
        form_data = {
            'username': username,
            'password': password,
        }
        payload = urlencode_postdata(form_data)
        request = sanitized_Request(self._LOGIN_URL, payload)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        login_page = self._download_webpage(
            request, None, False, 'Wrong login info')
        if not re.search(r'id="tubi-logout"', login_page):
            raise ExtractorError(
                'Login failed (invalid username/password)', expected=True)

    def _real_initialize(self):
        self._login()

    def _real_extract(self, url):
        video_id = self._match_id(url)
        video_data = self._download_json(
            'http://tubitv.com/oz/videos/%s/content' % video_id, video_id)
        title = video_data['title']

        formats = self._extract_m3u8_formats(
            self._proto_relative_url(video_data['url']),
            video_id, 'mp4', 'm3u8_native')
        self._sort_formats(formats)

        thumbnails = []
        for thumbnail_url in video_data.get('thumbnails', []):
            if not thumbnail_url:
                continue
            thumbnails.append({
                'url': self._proto_relative_url(thumbnail_url),
            })

        subtitles = {}
        for sub in video_data.get('subtitles', []):
            sub_url = sub.get('url')
            if not sub_url:
                continue
            subtitles.setdefault(sub.get('lang', 'English'), []).append({
                'url': self._proto_relative_url(sub_url),
            })

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
            'subtitles': subtitles,
            'thumbnails': thumbnails,
            'description': video_data.get('description'),
            'duration': int_or_none(video_data.get('duration')),
            'uploader_id': video_data.get('publisher_id'),
        }
