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
from ..utils import int_or_none


class MinotoIE(InfoExtractor):
    _VALID_URL = r'(?:minoto:|https?://(?:play|iframe|embed)\.minoto-video\.com/(?P<player_id>[0-9]+)/)(?P<id>[a-zA-Z0-9]+)'

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        player_id = mobj.group('player_id') or '1'
        video_id = mobj.group('id')
        video_data = self._download_json('http://play.minoto-video.com/%s/%s.js' % (player_id, video_id), video_id)
        video_metadata = video_data['video-metadata']
        formats = []
        for fmt in video_data['video-files']:
            fmt_url = fmt.get('url')
            if not fmt_url:
                continue
            container = fmt.get('container')
            if container == 'hls':
                formats.extend(fmt_url, video_id, 'mp4', m3u8_id='hls', fatal=False)
            else:
                fmt_profile = fmt.get('profile') or {}
                f = {
                    'format_id': fmt_profile.get('name-short'),
                    'format_note': fmt_profile.get('name'),
                    'url': fmt_url,
                    'container': container,
                    'tbr': int_or_none(fmt.get('bitrate')),
                    'filesize': int_or_none(fmt.get('filesize')),
                    'width': int_or_none(fmt.get('width')),
                    'height': int_or_none(fmt.get('height')),
                }
                codecs = fmt.get('codecs')
                if codecs:
                    codecs = codecs.split(',')
                    if len(codecs) == 2:
                        f.update({
                            'vcodec': codecs[0],
                            'acodec': codecs[1],
                        })
                formats.append(f)
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': video_metadata['title'],
            'description': video_metadata.get('description'),
            'thumbnail': video_metadata.get('video-poster', {}).get('url'),
            'formats': formats,
        }
