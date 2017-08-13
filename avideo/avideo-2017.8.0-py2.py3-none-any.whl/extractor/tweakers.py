
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
    determine_ext,
    mimetype2ext,
)


class TweakersIE(InfoExtractor):
    _VALID_URL = r'https?://tweakers\.net/video/(?P<id>\d+)'
    _TEST = {
        'url': 'https://tweakers.net/video/9926/new-nintendo-3ds-xl-op-alle-fronten-beter.html',
        'md5': 'fe73e417c093a788e0160c4025f88b15',
        'info_dict': {
            'id': '9926',
            'ext': 'mp4',
            'title': 'New Nintendo 3DS XL - Op alle fronten beter',
            'description': 'md5:3789b21fed9c0219e9bcaacd43fab280',
            'thumbnail': r're:^https?://.*\.jpe?g$',
            'duration': 386,
            'uploader_id': 's7JeEm',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        video_data = self._download_json(
            'https://tweakers.net/video/s1playlist/%s/1920/1080/playlist.json' % video_id,
            video_id)['items'][0]

        title = video_data['title']

        formats = []
        for location in video_data.get('locations', {}).get('progressive', []):
            format_id = location.get('label')
            width = int_or_none(location.get('width'))
            height = int_or_none(location.get('height'))
            for source in location.get('sources', []):
                source_url = source.get('src')
                if not source_url:
                    continue
                ext = mimetype2ext(source.get('type')) or determine_ext(source_url)
                formats.append({
                    'format_id': format_id,
                    'url': source_url,
                    'width': width,
                    'height': height,
                    'ext': ext,
                })
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'description': video_data.get('description'),
            'thumbnail': video_data.get('poster'),
            'duration': int_or_none(video_data.get('duration')),
            'uploader_id': video_data.get('account'),
            'formats': formats,
        }
