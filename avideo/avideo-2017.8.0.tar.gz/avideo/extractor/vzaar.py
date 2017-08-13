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
    int_or_none,
    float_or_none,
)


class VzaarIE(InfoExtractor):
    _VALID_URL = r'https?://(?:(?:www|view)\.)?vzaar\.com/(?:videos/)?(?P<id>\d+)'
    _TESTS = [{
        'url': 'https://vzaar.com/videos/1152805',
        'md5': 'bde5ddfeb104a6c56a93a06b04901dbf',
        'info_dict': {
            'id': '1152805',
            'ext': 'mp4',
            'title': 'sample video (public)',
        },
    }, {
        'url': 'https://view.vzaar.com/27272/player',
        'md5': '3b50012ac9bbce7f445550d54e0508f2',
        'info_dict': {
            'id': '27272',
            'ext': 'mp3',
            'title': 'MP3',
        },
    }]

    @staticmethod
    def _extract_urls(webpage):
        return re.findall(
            r'<iframe[^>]+src=["\']((?:https?:)?//(?:view\.vzaar\.com)/[0-9]+)',
            webpage)

    def _real_extract(self, url):
        video_id = self._match_id(url)
        video_data = self._download_json(
            'http://view.vzaar.com/v2/%s/video' % video_id, video_id)
        source_url = video_data['sourceUrl']

        info = {
            'id': video_id,
            'title': video_data['videoTitle'],
            'url': source_url,
            'thumbnail': self._proto_relative_url(video_data.get('poster')),
            'duration': float_or_none(video_data.get('videoDuration')),
        }
        if 'audio' in source_url:
            info.update({
                'vcodec': 'none',
                'ext': 'mp3',
            })
        else:
            info.update({
                'width': int_or_none(video_data.get('width')),
                'height': int_or_none(video_data.get('height')),
                'ext': 'mp4',
            })
        return info
