
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


class RadioDeIE(InfoExtractor):
    IE_NAME = 'radio.de'
    _VALID_URL = r'https?://(?P<id>.+?)\.(?:radio\.(?:de|at|fr|pt|es|pl|it)|rad\.io)'
    _TEST = {
        'url': 'http://ndr2.radio.de/',
        'info_dict': {
            'id': 'ndr2',
            'ext': 'mp3',
            'title': 're:^NDR 2 [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$',
            'description': 'md5:591c49c702db1a33751625ebfb67f273',
            'thumbnail': r're:^https?://.*\.png',
            'is_live': True,
        },
        'params': {
            'skip_download': True,
        }
    }

    def _real_extract(self, url):
        radio_id = self._match_id(url)
        webpage = self._download_webpage(url, radio_id)
        jscode = self._search_regex(
            r"'components/station/stationService':\s*\{\s*'?station'?:\s*(\{.*?\s*\}),\n",
            webpage, 'broadcast')

        broadcast = self._parse_json(jscode, radio_id)
        title = self._live_title(broadcast['name'])
        description = broadcast.get('description') or broadcast.get('shortDescription')
        thumbnail = broadcast.get('picture4Url') or broadcast.get('picture4TransUrl') or broadcast.get('logo100x100')

        formats = [{
            'url': stream['streamUrl'],
            'ext': stream['streamContentFormat'].lower(),
            'acodec': stream['streamContentFormat'],
            'abr': stream['bitRate'],
            'asr': stream['sampleRate']
        } for stream in broadcast['streamUrls']]
        self._sort_formats(formats)

        return {
            'id': radio_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'is_live': True,
            'formats': formats,
        }
