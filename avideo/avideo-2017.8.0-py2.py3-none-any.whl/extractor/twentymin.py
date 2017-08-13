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
    try_get,
)


class TwentyMinutenIE(InfoExtractor):
    IE_NAME = '20min'
    _VALID_URL = r'''(?x)
                    https?://
                        (?:www\.)?20min\.ch/
                        (?:
                            videotv/*\?.*?\bvid=|
                            videoplayer/videoplayer\.html\?.*?\bvideoId@
                        )
                        (?P<id>\d+)
                    '''
    _TESTS = [{
        'url': 'http://www.20min.ch/videotv/?vid=469148&cid=2',
        'md5': 'e7264320db31eed8c38364150c12496e',
        'info_dict': {
            'id': '469148',
            'ext': 'mp4',
            'title': '85 000 Franken für 15 perfekte Minuten',
            'thumbnail': r're:https?://.*\.jpg$',
        },
    }, {
        'url': 'http://www.20min.ch/videoplayer/videoplayer.html?params=client@twentyDE|videoId@523629',
        'info_dict': {
            'id': '523629',
            'ext': 'mp4',
            'title': 'So kommen Sie bei Eis und Schnee sicher an',
            'description': 'md5:117c212f64b25e3d95747e5276863f7d',
            'thumbnail': r're:https?://.*\.jpg$',
        },
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'http://www.20min.ch/videotv/?cid=44&vid=468738',
        'only_matching': True,
    }]

    @staticmethod
    def _extract_urls(webpage):
        return [m.group('url') for m in re.finditer(
            r'<iframe[^>]+src=(["\'])(?P<url>(?:(?:https?:)?//)?(?:www\.)?20min\.ch/videoplayer/videoplayer.html\?.*?\bvideoId@\d+.*?)\1',
            webpage)]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        video = self._download_json(
            'http://api.20min.ch/video/%s/show' % video_id,
            video_id)['content']

        title = video['title']

        formats = [{
            'format_id': format_id,
            'url': 'http://podcast.20min-tv.ch/podcast/20min/%s%s.mp4' % (video_id, p),
            'quality': quality,
        } for quality, (format_id, p) in enumerate([('sd', ''), ('hd', 'h')])]
        self._sort_formats(formats)

        description = video.get('lead')
        thumbnail = video.get('thumbnail')

        def extract_count(kind):
            return try_get(
                video,
                lambda x: int_or_none(x['communityobject']['thumbs_%s' % kind]))

        like_count = extract_count('up')
        dislike_count = extract_count('down')

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'formats': formats,
        }
