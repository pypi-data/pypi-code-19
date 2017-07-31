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


class GlideIE(InfoExtractor):
    IE_DESC = 'Glide mobile video messages (glide.me)'
    _VALID_URL = r'https?://share\.glide\.me/(?P<id>[A-Za-z0-9\-=_+]+)'
    _TEST = {
        'url': 'http://share.glide.me/UZF8zlmuQbe4mr+7dCiQ0w==',
        'md5': '4466372687352851af2d131cfaa8a4c7',
        'info_dict': {
            'id': 'UZF8zlmuQbe4mr+7dCiQ0w==',
            'ext': 'mp4',
            'title': "Damon's Glide message",
            'thumbnail': r're:^https?://.*?\.cloudfront\.net/.*\.jpg$',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        title = self._html_search_regex(
            r'<title>(.+?)</title>', webpage,
            'title', default=None) or self._og_search_title(webpage)
        video_url = self._proto_relative_url(self._search_regex(
            r'<source[^>]+src=(["\'])(?P<url>.+?)\1',
            webpage, 'video URL', default=None,
            group='url')) or self._og_search_video_url(webpage)
        thumbnail = self._proto_relative_url(self._search_regex(
            r'<img[^>]+id=["\']video-thumbnail["\'][^>]+src=(["\'])(?P<url>.+?)\1',
            webpage, 'thumbnail url', default=None,
            group='url')) or self._og_search_thumbnail(webpage)

        return {
            'id': video_id,
            'title': title,
            'url': video_url,
            'thumbnail': thumbnail,
        }
