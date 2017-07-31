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
    unified_strdate,
)


class ClipfishIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?clipfish\.de/(?:[^/]+/)+video/(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://www.clipfish.de/special/ugly-americans/video/4343170/s01-e01-ugly-americans-date-in-der-hoelle/',
        'md5': 'b9a5dc46294154c1193e2d10e0c95693',
        'info_dict': {
            'id': '4343170',
            'ext': 'mp4',
            'title': 'S01 E01 - Ugly Americans - Date in der Hölle',
            'description': 'Mark Lilly arbeitet im Sozialdienst der Stadt New York und soll Immigranten bei ihrer Einbürgerung in die USA zur Seite stehen.',
            'upload_date': '20161005',
            'duration': 1291,
            'view_count': int,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        video_info = self._download_json(
            'http://www.clipfish.de/devapi/id/%s?format=json&apikey=hbbtv' % video_id,
            video_id)['items'][0]

        formats = []

        m3u8_url = video_info.get('media_videourl_hls')
        if m3u8_url:
            formats.append({
                'url': m3u8_url.replace('de.hls.fra.clipfish.de', 'hls.fra.clipfish.de'),
                'ext': 'mp4',
                'format_id': 'hls',
            })

        mp4_url = video_info.get('media_videourl')
        if mp4_url:
            formats.append({
                'url': mp4_url,
                'format_id': 'mp4',
                'width': int_or_none(video_info.get('width')),
                'height': int_or_none(video_info.get('height')),
                'tbr': int_or_none(video_info.get('bitrate')),
            })

        descr = video_info.get('descr')
        if descr:
            descr = descr.strip()

        return {
            'id': video_id,
            'title': video_info['title'],
            'description': descr,
            'formats': formats,
            'thumbnail': video_info.get('media_content_thumbnail_large') or video_info.get('media_thumbnail'),
            'duration': int_or_none(video_info.get('media_length')),
            'upload_date': unified_strdate(video_info.get('pubDate')),
            'view_count': int_or_none(video_info.get('media_views'))
        }
