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
    float_or_none,
    qualities,
    ExtractorError,
)


class GfycatIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?gfycat\.com/(?:ifr/)?(?P<id>[^/?#]+)'
    _TESTS = [{
        'url': 'http://gfycat.com/DeadlyDecisiveGermanpinscher',
        'info_dict': {
            'id': 'DeadlyDecisiveGermanpinscher',
            'ext': 'mp4',
            'title': 'Ghost in the Shell',
            'timestamp': 1410656006,
            'upload_date': '20140914',
            'uploader': 'anonymous',
            'duration': 10.4,
            'view_count': int,
            'like_count': int,
            'dislike_count': int,
            'categories': list,
            'age_limit': 0,
        }
    }, {
        'url': 'http://gfycat.com/ifr/JauntyTimelyAmazontreeboa',
        'info_dict': {
            'id': 'JauntyTimelyAmazontreeboa',
            'ext': 'mp4',
            'title': 'JauntyTimelyAmazontreeboa',
            'timestamp': 1411720126,
            'upload_date': '20140926',
            'uploader': 'anonymous',
            'duration': 3.52,
            'view_count': int,
            'like_count': int,
            'dislike_count': int,
            'categories': list,
            'age_limit': 0,
        }
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        gfy = self._download_json(
            'http://gfycat.com/cajax/get/%s' % video_id,
            video_id, 'Downloading video info')
        if 'error' in gfy:
            raise ExtractorError('Gfycat said: ' + gfy['error'], expected=True)
        gfy = gfy['gfyItem']

        title = gfy.get('title') or gfy['gfyName']
        description = gfy.get('description')
        timestamp = int_or_none(gfy.get('createDate'))
        uploader = gfy.get('userName')
        view_count = int_or_none(gfy.get('views'))
        like_count = int_or_none(gfy.get('likes'))
        dislike_count = int_or_none(gfy.get('dislikes'))
        age_limit = 18 if gfy.get('nsfw') == '1' else 0

        width = int_or_none(gfy.get('width'))
        height = int_or_none(gfy.get('height'))
        fps = int_or_none(gfy.get('frameRate'))
        num_frames = int_or_none(gfy.get('numFrames'))

        duration = float_or_none(num_frames, fps) if num_frames and fps else None

        categories = gfy.get('tags') or gfy.get('extraLemmas') or []

        FORMATS = ('gif', 'webm', 'mp4')
        quality = qualities(FORMATS)

        formats = []
        for format_id in FORMATS:
            video_url = gfy.get('%sUrl' % format_id)
            if not video_url:
                continue
            filesize = int_or_none(gfy.get('%sSize' % format_id))
            formats.append({
                'url': video_url,
                'format_id': format_id,
                'width': width,
                'height': height,
                'fps': fps,
                'filesize': filesize,
                'quality': quality(format_id),
            })
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'timestamp': timestamp,
            'uploader': uploader,
            'duration': duration,
            'view_count': view_count,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'categories': categories,
            'age_limit': age_limit,
            'formats': formats,
        }
