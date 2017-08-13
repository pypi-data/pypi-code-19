
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
    parse_duration,
    unified_strdate,
)


class CamWithHerIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?camwithher\.tv/view_video\.php\?.*\bviewkey=(?P<id>\w+)'

    _TESTS = [{
        'url': 'http://camwithher.tv/view_video.php?viewkey=6e9a24e2c0e842e1f177&page=&viewtype=&category=',
        'info_dict': {
            'id': '5644',
            'ext': 'flv',
            'title': 'Periscope Tease',
            'description': 'In the clouds teasing on periscope to my favorite song',
            'duration': 240,
            'view_count': int,
            'comment_count': int,
            'uploader': 'MileenaK',
            'upload_date': '20160322',
        },
        'params': {
            'skip_download': True,
        }
    }, {
        'url': 'http://camwithher.tv/view_video.php?viewkey=6dfd8b7c97531a459937',
        'only_matching': True,
    }, {
        'url': 'http://camwithher.tv/view_video.php?page=&viewkey=6e9a24e2c0e842e1f177&viewtype=&category=',
        'only_matching': True,
    }, {
        'url': 'http://camwithher.tv/view_video.php?viewkey=b6c3b5bea9515d1a1fc4&page=&viewtype=&category=mv',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        flv_id = self._html_search_regex(
            r'<a[^>]+href=["\']/download/\?v=(\d+)', webpage, 'video id')

        # Video URL construction algorithm is reverse-engineered from cwhplayer.swf
        rtmp_url = 'rtmp://camwithher.tv/clipshare/%s' % (
            ('mp4:%s.mp4' % flv_id) if int(flv_id) > 2010 else flv_id)

        title = self._html_search_regex(
            r'<div[^>]+style="float:left"[^>]*>\s*<h2>(.+?)</h2>', webpage, 'title')
        description = self._html_search_regex(
            r'>Description:</span>(.+?)</div>', webpage, 'description', default=None)

        runtime = self._search_regex(
            r'Runtime\s*:\s*(.+?) \|', webpage, 'duration', default=None)
        if runtime:
            runtime = re.sub(r'[\s-]', '', runtime)
        duration = parse_duration(runtime)
        view_count = int_or_none(self._search_regex(
            r'Views\s*:\s*(\d+)', webpage, 'view count', default=None))
        comment_count = int_or_none(self._search_regex(
            r'Comments\s*:\s*(\d+)', webpage, 'comment count', default=None))

        uploader = self._search_regex(
            r'Added by\s*:\s*<a[^>]+>([^<]+)</a>', webpage, 'uploader', default=None)
        upload_date = unified_strdate(self._search_regex(
            r'Added on\s*:\s*([\d-]+)', webpage, 'upload date', default=None))

        return {
            'id': flv_id,
            'url': rtmp_url,
            'ext': 'flv',
            'no_resume': True,
            'title': title,
            'description': description,
            'duration': duration,
            'view_count': view_count,
            'comment_count': comment_count,
            'uploader': uploader,
            'upload_date': upload_date,
        }
