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
    int_or_none,
    parse_duration,
    parse_filesize,
    sanitized_Request,
    urlencode_postdata,
)


class MinhatecaIE(InfoExtractor):
    _VALID_URL = r'https?://minhateca\.com\.br/[^?#]+,(?P<id>[0-9]+)\.'
    _TEST = {
        'url': 'http://minhateca.com.br/pereba/misc/youtube-dl+test+video,125848331.mp4(video)',
        'info_dict': {
            'id': '125848331',
            'ext': 'mp4',
            'title': 'youtube-dl test video',
            'thumbnail': r're:^https?://.*\.jpg$',
            'filesize_approx': 1530000,
            'duration': 9,
            'view_count': int,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        token = self._html_search_regex(
            r'<input name="__RequestVerificationToken".*?value="([^"]+)"',
            webpage, 'request token')
        token_data = [
            ('fileId', video_id),
            ('__RequestVerificationToken', token),
        ]
        req = sanitized_Request(
            'http://minhateca.com.br/action/License/Download',
            data=urlencode_postdata(token_data))
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        data = self._download_json(
            req, video_id, note='Downloading metadata')

        video_url = data['redirectUrl']
        title_str = self._html_search_regex(
            r'<h1.*?>(.*?)</h1>', webpage, 'title')
        title, _, ext = title_str.rpartition('.')
        filesize_approx = parse_filesize(self._html_search_regex(
            r'<p class="fileSize">(.*?)</p>',
            webpage, 'file size approximation', fatal=False))
        duration = parse_duration(self._html_search_regex(
            r'(?s)<p class="fileLeng[ht][th]">.*?class="bold">(.*?)<',
            webpage, 'duration', fatal=False))
        view_count = int_or_none(self._html_search_regex(
            r'<p class="downloadsCounter">([0-9]+)</p>',
            webpage, 'view count', fatal=False))

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'ext': ext,
            'filesize_approx': filesize_approx,
            'duration': duration,
            'view_count': view_count,
            'thumbnail': self._og_search_thumbnail(webpage),
        }
