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

from .onet import OnetBaseIE


class VODPlIE(OnetBaseIE):
    _VALID_URL = r'https?://vod\.pl/(?:[^/]+/)+(?P<id>[0-9a-zA-Z]+)'

    _TESTS = [{
        'url': 'https://vod.pl/filmy/chlopaki-nie-placza/3ep3jns',
        'md5': 'a7dc3b2f7faa2421aefb0ecaabf7ec74',
        'info_dict': {
            'id': '3ep3jns',
            'ext': 'mp4',
            'title': 'Chłopaki nie płaczą',
            'description': 'md5:f5f03b84712e55f5ac9f0a3f94445224',
            'timestamp': 1463415154,
            'duration': 5765,
            'upload_date': '20160516',
        },
    }, {
        'url': 'https://vod.pl/seriale/belfer-na-planie-praca-kamery-online/2c10heh',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        info_dict = self._extract_from_id(self._search_mvp_id(webpage), webpage)
        info_dict['id'] = video_id
        return info_dict
