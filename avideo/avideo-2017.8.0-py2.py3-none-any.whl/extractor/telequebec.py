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
from ..compat import compat_str
from ..utils import (
    int_or_none,
    smuggle_url,
    try_get,
)


class TeleQuebecIE(InfoExtractor):
    _VALID_URL = r'https?://zonevideo\.telequebec\.tv/media/(?P<id>\d+)'
    _TESTS = [{
        'url': 'http://zonevideo.telequebec.tv/media/20984/le-couronnement-de-new-york/couronnement-de-new-york',
        'md5': 'fe95a0957e5707b1b01f5013e725c90f',
        'info_dict': {
            'id': '20984',
            'ext': 'mp4',
            'title': 'Le couronnement de New York',
            'description': 'md5:f5b3d27a689ec6c1486132b2d687d432',
            'upload_date': '20170201',
            'timestamp': 1485972222,
        }
    }, {
        # no description
        'url': 'http://zonevideo.telequebec.tv/media/30261',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        media_id = self._match_id(url)
        media_data = self._download_json(
            'https://mnmedias.api.telequebec.tv/api/v2/media/' + media_id,
            media_id)['media']
        return {
            '_type': 'url_transparent',
            'id': media_id,
            'url': smuggle_url(
                'limelight:media:' + media_data['streamInfo']['sourceId'],
                {'geo_countries': ['CA']}),
            'title': media_data['title'],
            'description': try_get(
                media_data, lambda x: x['descriptions'][0]['text'], compat_str),
            'duration': int_or_none(
                media_data.get('durationInMilliseconds'), 1000),
            'ie_key': 'LimelightMedia',
        }
