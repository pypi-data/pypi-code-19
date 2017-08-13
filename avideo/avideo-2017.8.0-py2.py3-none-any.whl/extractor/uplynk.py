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
    float_or_none,
    ExtractorError,
)


class UplynkIE(InfoExtractor):
    IE_NAME = 'uplynk'
    _VALID_URL = r'https?://.*?\.uplynk\.com/(?P<path>ext/[0-9a-f]{32}/(?P<external_id>[^/?&]+)|(?P<id>[0-9a-f]{32}))\.(?:m3u8|json)(?:.*?\bpbs=(?P<session_id>[^&]+))?'
    _TEST = {
        'url': 'http://content.uplynk.com/e89eaf2ce9054aa89d92ddb2d817a52e.m3u8',
        'info_dict': {
            'id': 'e89eaf2ce9054aa89d92ddb2d817a52e',
            'ext': 'mp4',
            'title': '030816-kgo-530pm-solar-eclipse-vid_web.mp4',
            'uploader_id': '4413701bf5a1488db55b767f8ae9d4fa',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
    }

    def _extract_uplynk_info(self, uplynk_content_url):
        path, external_id, video_id, session_id = re.match(UplynkIE._VALID_URL, uplynk_content_url).groups()
        display_id = video_id or external_id
        formats = self._extract_m3u8_formats(
            'http://content.uplynk.com/%s.m3u8' % path,
            display_id, 'mp4', 'm3u8_native')
        if session_id:
            for f in formats:
                f['extra_param_to_segment_url'] = 'pbs=' + session_id
        self._sort_formats(formats)
        asset = self._download_json('http://content.uplynk.com/player/assetinfo/%s.json' % path, display_id)
        if asset.get('error') == 1:
            raise ExtractorError('% said: %s' % (self.IE_NAME, asset['msg']), expected=True)

        return {
            'id': asset['asset'],
            'title': asset['desc'],
            'thumbnail': asset.get('default_poster_url'),
            'duration': float_or_none(asset.get('duration')),
            'uploader_id': asset.get('owner'),
            'formats': formats,
        }

    def _real_extract(self, url):
        return self._extract_uplynk_info(url)


class UplynkPreplayIE(UplynkIE):
    IE_NAME = 'uplynk:preplay'
    _VALID_URL = r'https?://.*?\.uplynk\.com/preplay2?/(?P<path>ext/[0-9a-f]{32}/(?P<external_id>[^/?&]+)|(?P<id>[0-9a-f]{32}))\.json'
    _TEST = None

    def _real_extract(self, url):
        path, external_id, video_id = re.match(self._VALID_URL, url).groups()
        display_id = video_id or external_id
        preplay = self._download_json(url, display_id)
        content_url = 'http://content.uplynk.com/%s.m3u8' % path
        session_id = preplay.get('sid')
        if session_id:
            content_url += '?pbs=' + session_id
        return self._extract_uplynk_info(content_url)
