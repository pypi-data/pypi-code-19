
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
from ..utils import unified_strdate


class DFBIE(InfoExtractor):
    IE_NAME = 'tv.dfb.de'
    _VALID_URL = r'https?://tv\.dfb\.de/video/(?P<display_id>[^/]+)/(?P<id>\d+)'

    _TEST = {
        'url': 'http://tv.dfb.de/video/u-19-em-stimmen-zum-spiel-gegen-russland/11633/',
        'md5': 'ac0f98a52a330f700b4b3034ad240649',
        'info_dict': {
            'id': '11633',
            'display_id': 'u-19-em-stimmen-zum-spiel-gegen-russland',
            'ext': 'mp4',
            'title': 'U 19-EM: Stimmen zum Spiel gegen Russland',
            'upload_date': '20150714',
        },
    }

    def _real_extract(self, url):
        display_id, video_id = re.match(self._VALID_URL, url).groups()

        player_info = self._download_xml(
            'http://tv.dfb.de/server/hd_video.php?play=%s' % video_id,
            display_id)
        video_info = player_info.find('video')
        stream_access_url = self._proto_relative_url(video_info.find('url').text.strip())

        formats = []
        # see http://tv.dfb.de/player/js/ajax.js for the method to extract m3u8 formats
        for sa_url in (stream_access_url, stream_access_url + '&area=&format=iphone'):
            stream_access_info = self._download_xml(sa_url, display_id)
            token_el = stream_access_info.find('token')
            manifest_url = token_el.attrib['url'] + '?' + 'hdnea=' + token_el.attrib['auth']
            if '.f4m' in manifest_url:
                formats.extend(self._extract_f4m_formats(
                    manifest_url + '&hdcore=3.2.0',
                    display_id, f4m_id='hds', fatal=False))
            else:
                formats.extend(self._extract_m3u8_formats(
                    manifest_url, display_id, 'mp4',
                    'm3u8_native', m3u8_id='hls', fatal=False))
        self._sort_formats(formats)

        return {
            'id': video_id,
            'display_id': display_id,
            'title': video_info.find('title').text,
            'thumbnail': 'http://tv.dfb.de/images/%s_640x360.jpg' % video_id,
            'upload_date': unified_strdate(video_info.find('time_date').text),
            'formats': formats,
        }
