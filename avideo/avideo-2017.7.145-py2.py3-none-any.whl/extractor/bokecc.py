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
from ..compat import compat_parse_qs
from ..utils import ExtractorError


class BokeCCBaseIE(InfoExtractor):
    def _extract_bokecc_formats(self, webpage, video_id, format_id=None):
        player_params_str = self._html_search_regex(
            r'<(?:script|embed)[^>]+src="http://p\.bokecc\.com/player\?([^"]+)',
            webpage, 'player params')

        player_params = compat_parse_qs(player_params_str)

        info_xml = self._download_xml(
            'http://p.bokecc.com/servlet/playinfo?uid=%s&vid=%s&m=1' % (
                player_params['siteid'][0], player_params['vid'][0]), video_id)

        formats = [{
            'format_id': format_id,
            'url': quality.find('./copy').attrib['playurl'],
            'preference': int(quality.attrib['value']),
        } for quality in info_xml.findall('./video/quality')]

        self._sort_formats(formats)

        return formats


class BokeCCIE(BokeCCBaseIE):
    _IE_DESC = 'CC视频'
    _VALID_URL = r'https?://union\.bokecc\.com/playvideo\.bo\?(?P<query>.*)'

    _TESTS = [{
        'url': 'http://union.bokecc.com/playvideo.bo?vid=E44D40C15E65EA30&uid=CD0C5D3C8614B28B',
        'info_dict': {
            'id': 'CD0C5D3C8614B28B_E44D40C15E65EA30',
            'ext': 'flv',
            'title': 'BokeCC Video',
        },
    }]

    def _real_extract(self, url):
        qs = compat_parse_qs(re.match(self._VALID_URL, url).group('query'))
        if not qs.get('vid') or not qs.get('uid'):
            raise ExtractorError('Invalid URL', expected=True)

        video_id = '%s_%s' % (qs['uid'][0], qs['vid'][0])

        webpage = self._download_webpage(url, video_id)

        return {
            'id': video_id,
            'title': 'BokeCC Video',  # no title provided in the webpage
            'formats': self._extract_bokecc_formats(webpage, video_id),
        }
