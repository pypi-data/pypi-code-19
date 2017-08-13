
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
from ..compat import compat_str
from ..utils import (
    clean_html,
    float_or_none,
    int_or_none,
    try_get,
)


class HitRecordIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?hitrecord\.org/records/(?P<id>\d+)'
    _TEST = {
        'url': 'https://hitrecord.org/records/2954362',
        'md5': 'fe1cdc2023bce0bbb95c39c57426aa71',
        'info_dict': {
            'id': '2954362',
            'ext': 'mp4',
            'title': 'A Very Different World (HITRECORD x ACLU)',
            'description': 'md5:e62defaffab5075a5277736bead95a3d',
            'duration': 139.327,
            'timestamp': 1471557582,
            'upload_date': '20160818',
            'uploader': 'Zuzi.C12',
            'uploader_id': '362811',
            'view_count': int,
            'like_count': int,
            'comment_count': int,
            'tags': list,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        video = self._download_json(
            'https://hitrecord.org/api/web/records/%s' % video_id, video_id)

        title = video['title']
        video_url = video['source_url']['mp4_url']

        tags = None
        tags_list = try_get(video, lambda x: x['tags'], list)
        if tags_list:
            tags = [
                t['text']
                for t in tags_list
                if isinstance(t, dict) and t.get('text') and
                isinstance(t['text'], compat_str)]

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'description': clean_html(video.get('body')),
            'duration': float_or_none(video.get('duration'), 1000),
            'timestamp': int_or_none(video.get('created_at_i')),
            'uploader': try_get(
                video, lambda x: x['user']['username'], compat_str),
            'uploader_id': try_get(
                video, lambda x: compat_str(x['user']['id'])),
            'view_count': int_or_none(video.get('total_views_count')),
            'like_count': int_or_none(video.get('hearts_count')),
            'comment_count': int_or_none(video.get('comments_count')),
            'tags': tags,
        }
