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
    determine_ext,
    int_or_none,
    unescapeHTML,
)


class ATVAtIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?atv\.at/(?:[^/]+/){2}(?P<id>[dv]\d+)'
    _TESTS = [{
        'url': 'http://atv.at/aktuell/di-210317-2005-uhr/v1698449/',
        'md5': 'c3b6b975fb3150fc628572939df205f2',
        'info_dict': {
            'id': '1698447',
            'ext': 'mp4',
            'title': 'DI, 21.03.17 | 20:05 Uhr 1/1',
        }
    }, {
        'url': 'http://atv.at/aktuell/meinrad-knapp/d8416/',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        video_data = self._parse_json(unescapeHTML(self._search_regex(
            r'class="[^"]*jsb_video/FlashPlayer[^"]*"[^>]+data-jsb="([^"]+)"',
            webpage, 'player data')), display_id)['config']['initial_video']

        video_id = video_data['id']
        video_title = video_data['title']

        parts = []
        for part in video_data.get('parts', []):
            part_id = part['id']
            part_title = part['title']

            formats = []
            for source in part.get('sources', []):
                source_url = source.get('src')
                if not source_url:
                    continue
                ext = determine_ext(source_url)
                if ext == 'm3u8':
                    formats.extend(self._extract_m3u8_formats(
                        source_url, part_id, 'mp4', 'm3u8_native',
                        m3u8_id='hls', fatal=False))
                else:
                    formats.append({
                        'format_id': source.get('delivery'),
                        'url': source_url,
                    })
            self._sort_formats(formats)

            parts.append({
                'id': part_id,
                'title': part_title,
                'thumbnail': part.get('preview_image_url'),
                'duration': int_or_none(part.get('duration')),
                'is_live': part.get('is_livestream'),
                'formats': formats,
            })

        return {
            '_type': 'multi_video',
            'id': video_id,
            'title': video_title,
            'entries': parts,
        }
