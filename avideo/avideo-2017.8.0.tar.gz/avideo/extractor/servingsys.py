
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
)


class ServingSysIE(InfoExtractor):
    _VALID_URL = r'https?://(?:[^.]+\.)?serving-sys\.com/BurstingPipe/adServer\.bs\?.*?&pli=(?P<id>[0-9]+)'

    _TEST = {
        'url': 'http://bs.serving-sys.com/BurstingPipe/adServer.bs?cn=is&c=23&pl=VAST&pli=5349193&PluID=0&pos=7135&ord=[timestamp]&cim=1?',
        'info_dict': {
            'id': '5349193',
            'title': 'AdAPPter_Hyundai_demo',
        },
        'playlist': [{
            'md5': 'baed851342df6846eb8677a60a011a0f',
            'info_dict': {
                'id': '29955898',
                'ext': 'flv',
                'title': 'AdAPPter_Hyundai_demo (1)',
                'duration': 74,
                'tbr': 1378,
                'width': 640,
                'height': 400,
            },
        }, {
            'md5': '979b4da2655c4bc2d81aeb915a8c5014',
            'info_dict': {
                'id': '29907998',
                'ext': 'flv',
                'title': 'AdAPPter_Hyundai_demo (2)',
                'duration': 34,
                'width': 854,
                'height': 480,
                'tbr': 516,
            },
        }],
        'params': {
            'playlistend': 2,
        },
        '_skip': 'Blocked in the US [sic]',
    }

    def _real_extract(self, url):
        pl_id = self._match_id(url)
        vast_doc = self._download_xml(url, pl_id)

        title = vast_doc.find('.//AdTitle').text
        media = vast_doc.find('.//MediaFile').text
        info_url = self._search_regex(r'&adData=([^&]+)&', media, 'info URL')

        doc = self._download_xml(info_url, pl_id, 'Downloading video info')
        entries = [{
            '_type': 'video',
            'id': a.attrib['id'],
            'title': '%s (%s)' % (title, a.attrib['assetID']),
            'url': a.attrib['URL'],
            'duration': int_or_none(a.attrib.get('length')),
            'tbr': int_or_none(a.attrib.get('bitrate')),
            'height': int_or_none(a.attrib.get('height')),
            'width': int_or_none(a.attrib.get('width')),
        } for a in doc.findall('.//AdditionalAssets/asset')]

        return {
            '_type': 'playlist',
            'id': pl_id,
            'title': title,
            'entries': entries,
        }
