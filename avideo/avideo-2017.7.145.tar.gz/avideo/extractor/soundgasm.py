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


class SoundgasmIE(InfoExtractor):
    IE_NAME = 'soundgasm'
    _VALID_URL = r'https?://(?:www\.)?soundgasm\.net/u/(?P<user>[0-9a-zA-Z_\-]+)/(?P<title>[0-9a-zA-Z_\-]+)'
    _TEST = {
        'url': 'http://soundgasm.net/u/ytdl/Piano-sample',
        'md5': '010082a2c802c5275bb00030743e75ad',
        'info_dict': {
            'id': '88abd86ea000cafe98f96321b23cc1206cbcbcc9',
            'ext': 'm4a',
            'title': 'ytdl_Piano-sample',
            'description': 'Royalty Free Sample Music'
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        display_id = mobj.group('title')
        audio_title = mobj.group('user') + '_' + mobj.group('title')
        webpage = self._download_webpage(url, display_id)
        audio_url = self._html_search_regex(
            r'(?s)m4a\:\s"([^"]+)"', webpage, 'audio URL')
        audio_id = re.split(r'\/|\.', audio_url)[-2]
        description = self._html_search_regex(
            r'(?s)<li>Description:\s(.*?)<\/li>', webpage, 'description',
            fatal=False)

        return {
            'id': audio_id,
            'display_id': display_id,
            'url': audio_url,
            'title': audio_title,
            'description': description
        }


class SoundgasmProfileIE(InfoExtractor):
    IE_NAME = 'soundgasm:profile'
    _VALID_URL = r'https?://(?:www\.)?soundgasm\.net/u/(?P<id>[^/]+)/?(?:\#.*)?$'
    _TEST = {
        'url': 'http://soundgasm.net/u/ytdl',
        'info_dict': {
            'id': 'ytdl',
        },
        'playlist_count': 1,
    }

    def _real_extract(self, url):
        profile_id = self._match_id(url)

        webpage = self._download_webpage(url, profile_id)

        entries = [
            self.url_result(audio_url, 'Soundgasm')
            for audio_url in re.findall(r'href="([^"]+/u/%s/[^"]+)' % profile_id, webpage)]

        return self.playlist_result(entries, profile_id)
