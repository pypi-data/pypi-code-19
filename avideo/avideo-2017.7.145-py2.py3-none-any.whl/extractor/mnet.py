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
    parse_duration,
    parse_iso8601,
)


class MnetIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?mnet\.(?:com|interest\.me)/tv/vod/(?:.*?\bclip_id=)?(?P<id>[0-9]+)'
    _TESTS = [{
        'url': 'http://www.mnet.com/tv/vod/171008',
        'info_dict': {
            'id': '171008',
            'title': 'SS_이해인@히든박스',
            'description': 'md5:b9efa592c3918b615ba69fe9f8a05c55',
            'duration': 88,
            'upload_date': '20151231',
            'timestamp': 1451564040,
            'age_limit': 0,
            'thumbnails': 'mincount:5',
            'thumbnail': r're:^https?://.*\.jpg$',
            'ext': 'flv',
        },
        'params': {
            # rtmp download
            'skip_download': True,
        },
    }, {
        'url': 'http://mnet.interest.me/tv/vod/172790',
        'only_matching': True,
    }, {
        'url': 'http://www.mnet.com/tv/vod/vod_view.asp?clip_id=172790&tabMenu=',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        info = self._download_json(
            'http://content.api.mnet.com/player/vodConfig?id=%s&ctype=CLIP' % video_id,
            video_id, 'Downloading vod config JSON')['data']['info']

        title = info['title']

        rtmp_info = self._download_json(
            info['cdn'], video_id, 'Downloading vod cdn JSON')

        formats = [{
            'url': rtmp_info['serverurl'] + rtmp_info['fileurl'],
            'ext': 'flv',
            'page_url': url,
            'player_url': 'http://flvfile.mnet.com/service/player/201602/cjem_player_tv.swf?v=201602191318',
        }]

        description = info.get('ment')
        duration = parse_duration(info.get('time'))
        timestamp = parse_iso8601(info.get('date'), delimiter=' ')
        age_limit = info.get('adult')
        if age_limit is not None:
            age_limit = 0 if age_limit == 'N' else 18
        thumbnails = [{
            'id': thumb_format,
            'url': thumb['url'],
            'width': int_or_none(thumb.get('width')),
            'height': int_or_none(thumb.get('height')),
        } for thumb_format, thumb in info.get('cover', {}).items() if thumb.get('url')]

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'duration': duration,
            'timestamp': timestamp,
            'age_limit': age_limit,
            'thumbnails': thumbnails,
            'formats': formats,
        }
