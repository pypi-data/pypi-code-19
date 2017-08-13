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
from ..compat import compat_urlparse
from ..utils import (
    get_element_by_attribute,
    qualities,
    unescapeHTML,
)


class OraTVIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?(?:ora\.tv|unsafespeech\.com)/([^/]+/)*(?P<id>[^/\?#]+)'
    _TESTS = [{
        'url': 'https://www.ora.tv/larrykingnow/2015/12/16/vine-youtube-stars-zach-king-king-bach-on-their-viral-videos-0_36jupg6090pq',
        'md5': 'fa33717591c631ec93b04b0e330df786',
        'info_dict': {
            'id': '50178',
            'ext': 'mp4',
            'title': 'Vine & YouTube Stars Zach King & King Bach On Their Viral Videos!',
            'description': 'md5:ebbc5b1424dd5dba7be7538148287ac1',
        }
    }, {
        'url': 'http://www.unsafespeech.com/video/2016/5/10/student-self-censorship-and-the-thought-police-on-university-campuses-0_6622bnkppw4d',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        video_data = self._search_regex(
            r'"(?:video|current)"\s*:\s*({[^}]+?})', webpage, 'current video')
        m3u8_url = self._search_regex(
            r'hls_stream"?\s*:\s*"([^"]+)', video_data, 'm3u8 url', None)
        if m3u8_url:
            formats = self._extract_m3u8_formats(
                m3u8_url, display_id, 'mp4', 'm3u8_native',
                m3u8_id='hls', fatal=False)
            # similar to GameSpotIE
            m3u8_path = compat_urlparse.urlparse(m3u8_url).path
            QUALITIES_RE = r'((,[a-z]+\d+)+,?)'
            available_qualities = self._search_regex(
                QUALITIES_RE, m3u8_path, 'qualities').strip(',').split(',')
            http_path = m3u8_path[1:].split('/', 1)[1]
            http_template = re.sub(QUALITIES_RE, r'%s', http_path)
            http_template = http_template.replace('.csmil/master.m3u8', '')
            http_template = compat_urlparse.urljoin(
                'http://videocdn-pmd.ora.tv/', http_template)
            preference = qualities(
                ['mobile400', 'basic400', 'basic600', 'sd900', 'sd1200', 'sd1500', 'hd720', 'hd1080'])
            for q in available_qualities:
                formats.append({
                    'url': http_template % q,
                    'format_id': q,
                    'preference': preference(q),
                })
            self._sort_formats(formats)
        else:
            return self.url_result(self._search_regex(
                r'"youtube_id"\s*:\s*"([^"]+)', webpage, 'youtube id'), 'Youtube')

        return {
            'id': self._search_regex(
                r'"id"\s*:\s*(\d+)', video_data, 'video id', default=display_id),
            'display_id': display_id,
            'title': unescapeHTML(self._og_search_title(webpage)),
            'description': get_element_by_attribute(
                'class', 'video_txt_decription', webpage),
            'thumbnail': self._proto_relative_url(self._search_regex(
                r'"thumb"\s*:\s*"([^"]+)', video_data, 'thumbnail', None)),
            'formats': formats,
        }
