
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
    parse_iso8601,
)


class VideofyMeIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.videofy\.me/.+?|p\.videofy\.me/v)/(?P<id>\d+)(&|#|$)'
    IE_NAME = 'videofy.me'

    _TEST = {
        'url': 'http://www.videofy.me/thisisvideofyme/1100701',
        'md5': 'c77d700bdc16ae2e9f3c26019bd96143',
        'info_dict': {
            'id': '1100701',
            'ext': 'mp4',
            'title': 'This is VideofyMe',
            'description': '',
            'upload_date': '20130326',
            'timestamp': 1364288959,
            'uploader': 'VideofyMe',
            'uploader_id': 'thisisvideofyme',
            'view_count': int,
            'likes': int,
            'comment_count': int,
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        config = self._download_json('http://vf-player-info-loader.herokuapp.com/%s.json' % video_id, video_id)['videoinfo']

        video = config.get('video')
        blog = config.get('blog', {})

        return {
            'id': video_id,
            'title': video['title'],
            'url': video['sources']['source']['url'],
            'thumbnail': video.get('thumb'),
            'description': video.get('description'),
            'timestamp': parse_iso8601(video.get('date')),
            'uploader': blog.get('name'),
            'uploader_id': blog.get('identifier'),
            'view_count': int_or_none(self._search_regex(r'([0-9]+)', video.get('views'), 'view count', fatal=False)),
            'likes': int_or_none(video.get('likes')),
            'comment_count': int_or_none(video.get('nrOfComments')),
        }
