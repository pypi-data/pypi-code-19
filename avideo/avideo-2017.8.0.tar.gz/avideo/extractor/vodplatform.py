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
from ..utils import unescapeHTML


class VODPlatformIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?vod-platform\.net/[eE]mbed/(?P<id>[^/?#]+)'
    _TEST = {
        # from http://www.lbcgroup.tv/watch/chapter/29143/52844/%D8%A7%D9%84%D9%86%D8%B5%D8%B1%D8%A9-%D9%81%D9%8A-%D8%B6%D9%8A%D8%A7%D9%81%D8%A9-%D8%A7%D9%84%D9%80-cnn/ar
        'url': 'http://vod-platform.net/embed/RufMcytHDolTH1MuKHY9Fw',
        'md5': '1db2b7249ce383d6be96499006e951fc',
        'info_dict': {
            'id': 'RufMcytHDolTH1MuKHY9Fw',
            'ext': 'mp4',
            'title': 'LBCi News_ النصرة في ضيافة الـ "سي.أن.أن"',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        title = unescapeHTML(self._og_search_title(webpage))
        hidden_inputs = self._hidden_inputs(webpage)

        formats = self._extract_wowza_formats(
            hidden_inputs.get('HiddenmyhHlsLink') or hidden_inputs['HiddenmyDashLink'], video_id, skip_protocols=['f4m', 'smil'])
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'thumbnail': hidden_inputs.get('HiddenThumbnail') or self._og_search_thumbnail(webpage),
            'formats': formats,
        }
