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
from ..utils import (
    int_or_none,
    urljoin,
)


class MelonVODIE(InfoExtractor):
    _VALID_URL = r'https?://vod\.melon\.com/video/detail2\.html?\?.*?mvId=(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://vod.melon.com/video/detail2.htm?mvId=50158734',
        'info_dict': {
            'id': '50158734',
            'ext': 'mp4',
            'title': "Jessica 'Wonderland' MV Making Film",
            'thumbnail': r're:^https?://.*\.jpg$',
            'artist': 'Jessica (제시카)',
            'upload_date': '20161212',
            'duration': 203,
        },
        'params': {
            'skip_download': 'm3u8 download',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        play_info = self._download_json(
            'http://vod.melon.com/video/playerInfo.json', video_id,
            note='Downloading player info JSON', query={'mvId': video_id})

        title = play_info['mvInfo']['MVTITLE']

        info = self._download_json(
            'http://vod.melon.com/delivery/streamingInfo.json', video_id,
            note='Downloading streaming info JSON',
            query={
                'contsId': video_id,
                'contsType': 'VIDEO',
            })

        stream_info = info['streamingInfo']

        formats = self._extract_m3u8_formats(
            stream_info['encUrl'], video_id, 'mp4', m3u8_id='hls')
        self._sort_formats(formats)

        artist_list = play_info.get('artistList')
        artist = None
        if isinstance(artist_list, list):
            artist = ', '.join(
                [a['ARTISTNAMEWEBLIST']
                 for a in artist_list if a.get('ARTISTNAMEWEBLIST')])

        thumbnail = urljoin(info.get('staticDomain'), stream_info.get('imgPath'))

        duration = int_or_none(stream_info.get('playTime'))
        upload_date = stream_info.get('mvSvcOpenDt', '')[:8] or None

        return {
            'id': video_id,
            'title': title,
            'artist': artist,
            'thumbnail': thumbnail,
            'upload_date': upload_date,
            'duration': duration,
            'formats': formats
        }
