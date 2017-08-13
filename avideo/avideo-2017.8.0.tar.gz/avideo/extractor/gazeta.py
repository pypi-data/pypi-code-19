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


class GazetaIE(InfoExtractor):
    _VALID_URL = r'(?P<url>https?://(?:www\.)?gazeta\.ru/(?:[^/]+/)?video/(?:main/)*(?:\d{4}/\d{2}/\d{2}/)?(?P<id>[A-Za-z0-9-_.]+)\.s?html)'
    _TESTS = [{
        'url': 'http://www.gazeta.ru/video/main/zadaite_vopros_vladislavu_yurevichu.shtml',
        'md5': 'd49c9bdc6e5a7888f27475dc215ee789',
        'info_dict': {
            'id': '205566',
            'ext': 'mp4',
            'title': '«70–80 процентов гражданских в Донецке на грани голода»',
            'description': 'md5:38617526050bd17b234728e7f9620a71',
            'thumbnail': r're:^https?://.*\.jpg',
        },
        'skip': 'video not found',
    }, {
        'url': 'http://www.gazeta.ru/lifestyle/video/2015/03/08/master-klass_krasivoi_byt._delaem_vesennii_makiyazh.shtml',
        'only_matching': True,
    }, {
        'url': 'http://www.gazeta.ru/video/main/main/2015/06/22/platit_ili_ne_platit_po_isku_yukosa.shtml',
        'md5': '37f19f78355eb2f4256ee1688359f24c',
        'info_dict': {
            'id': '252048',
            'ext': 'mp4',
            'title': '"Если по иску ЮКОСа придется платить, это будет большой удар по бюджету"',
        },
        'add_ie': ['EaglePlatform'],
    }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)

        display_id = mobj.group('id')
        embed_url = '%s?p=embed' % mobj.group('url')
        embed_page = self._download_webpage(
            embed_url, display_id, 'Downloading embed page')

        video_id = self._search_regex(
            r'<div[^>]*?class="eagleplayer"[^>]*?data-id="([^"]+)"', embed_page, 'video id')

        return self.url_result(
            'eagleplatform:gazeta.media.eagleplatform.com:%s' % video_id, 'EaglePlatform')
