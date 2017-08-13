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

import json
import re

from .common import InfoExtractor
from ..utils import (
    determine_ext,
    int_or_none,
    js_to_json,
)
from ..compat import compat_urlparse


class UDNEmbedIE(InfoExtractor):
    IE_DESC = '聯合影音'
    _PROTOCOL_RELATIVE_VALID_URL = r'//video\.udn\.com/(?:embed|play)/news/(?P<id>\d+)'
    _VALID_URL = r'https?:' + _PROTOCOL_RELATIVE_VALID_URL
    _TESTS = [{
        'url': 'http://video.udn.com/embed/news/300040',
        'info_dict': {
            'id': '300040',
            'ext': 'mp4',
            'title': '生物老師男變女 全校挺"做自己"',
            'thumbnail': r're:^https?://.*\.jpg$',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
    }, {
        'url': 'https://video.udn.com/embed/news/300040',
        'only_matching': True,
    }, {
        # From https://video.udn.com/news/303776
        'url': 'https://video.udn.com/play/news/303776',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        page = self._download_webpage(url, video_id)

        options = json.loads(js_to_json(self._html_search_regex(
            r'var\s+options\s*=\s*([^;]+);', page, 'video urls dictionary')))

        video_urls = options['video']

        if video_urls.get('youtube'):
            return self.url_result(video_urls.get('youtube'), 'Youtube')

        formats = []
        for video_type, api_url in video_urls.items():
            if not api_url:
                continue

            video_url = self._download_webpage(
                compat_urlparse.urljoin(url, api_url), video_id,
                note='retrieve url for %s video' % video_type)

            ext = determine_ext(video_url)
            if ext == 'm3u8':
                formats.extend(self._extract_m3u8_formats(
                    video_url, video_id, ext='mp4', m3u8_id='hls'))
            elif ext == 'f4m':
                formats.extend(self._extract_f4m_formats(
                    video_url, video_id, f4m_id='hds'))
            else:
                mobj = re.search(r'_(?P<height>\d+)p_(?P<tbr>\d+).mp4', video_url)
                a_format = {
                    'url': video_url,
                    # video_type may be 'mp4', which confuses YoutubeDL
                    'format_id': 'http-' + video_type,
                }
                if mobj:
                    a_format.update({
                        'height': int_or_none(mobj.group('height')),
                        'tbr': int_or_none(mobj.group('tbr')),
                    })
                formats.append(a_format)

        self._sort_formats(formats)

        thumbnails = [{
            'url': img_url,
            'id': img_type,
        } for img_type, img_url in options.get('gallery', [{}])[0].items() if img_url]

        return {
            'id': video_id,
            'formats': formats,
            'title': options['title'],
            'thumbnails': thumbnails,
        }
