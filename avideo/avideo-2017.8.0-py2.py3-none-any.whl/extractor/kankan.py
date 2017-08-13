
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
import hashlib

from .common import InfoExtractor

_md5 = lambda s: hashlib.md5(s.encode('utf-8')).hexdigest()


class KankanIE(InfoExtractor):
    _VALID_URL = r'https?://(?:.*?\.)?kankan\.com/.+?/(?P<id>\d+)\.shtml'

    _TEST = {
        'url': 'http://yinyue.kankan.com/vod/48/48863.shtml',
        'md5': '29aca1e47ae68fc28804aca89f29507e',
        'info_dict': {
            'id': '48863',
            'ext': 'flv',
            'title': 'Ready To Go',
        },
        'skip': 'Only available from China',
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        title = self._search_regex(r'(?:G_TITLE=|G_MOVIE_TITLE = )[\'"](.+?)[\'"]', webpage, 'video title')
        surls = re.search(r'surls:\[\'.+?\'\]|lurl:\'.+?\.flv\'', webpage).group(0)
        gcids = re.findall(r'http://.+?/.+?/(.+?)/', surls)
        gcid = gcids[-1]

        info_url = 'http://p2s.cl.kankan.com/getCdnresource_flv?gcid=%s' % gcid
        video_info_page = self._download_webpage(
            info_url, video_id, 'Downloading video url info')
        ip = self._search_regex(r'ip:"(.+?)"', video_info_page, 'video url ip')
        path = self._search_regex(r'path:"(.+?)"', video_info_page, 'video url path')
        param1 = self._search_regex(r'param1:(\d+)', video_info_page, 'param1')
        param2 = self._search_regex(r'param2:(\d+)', video_info_page, 'param2')
        key = _md5('xl_mp43651' + param1 + param2)
        video_url = 'http://%s%s?key=%s&key1=%s' % (ip, path, key, param2)

        return {
            'id': video_id,
            'title': title,
            'url': video_url,
        }
