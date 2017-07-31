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
    ExtractorError,
    float_or_none,
    srt_subtitles_timecode,
)


class KanalPlayIE(InfoExtractor):
    IE_DESC = 'Kanal 5/9/11 Play'
    _VALID_URL = r'https?://(?:www\.)?kanal(?P<channel_id>5|9|11)play\.se/(?:#!/)?(?:play/)?program/\d+/video/(?P<id>\d+)'
    _TESTS = [{
        'url': 'http://www.kanal5play.se/#!/play/program/3060212363/video/3270012277',
        'info_dict': {
            'id': '3270012277',
            'ext': 'flv',
            'title': 'Saknar både dusch och avlopp',
            'description': 'md5:6023a95832a06059832ae93bc3c7efb7',
            'duration': 2636.36,
        },
        'params': {
            # rtmp download
            'skip_download': True,
        }
    }, {
        'url': 'http://www.kanal9play.se/#!/play/program/335032/video/246042',
        'only_matching': True,
    }, {
        'url': 'http://www.kanal11play.se/#!/play/program/232835958/video/367135199',
        'only_matching': True,
    }]

    def _fix_subtitles(self, subs):
        return '\r\n\r\n'.join(
            '%s\r\n%s --> %s\r\n%s'
            % (
                num,
                srt_subtitles_timecode(item['startMillis'] / 1000.0),
                srt_subtitles_timecode(item['endMillis'] / 1000.0),
                item['text'],
            ) for num, item in enumerate(subs, 1))

    def _get_subtitles(self, channel_id, video_id):
        subs = self._download_json(
            'http://www.kanal%splay.se/api/subtitles/%s' % (channel_id, video_id),
            video_id, 'Downloading subtitles JSON', fatal=False)
        return {'sv': [{'ext': 'srt', 'data': self._fix_subtitles(subs)}]} if subs else {}

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        channel_id = mobj.group('channel_id')

        video = self._download_json(
            'http://www.kanal%splay.se/api/getVideo?format=FLASH&videoId=%s' % (channel_id, video_id),
            video_id)

        reasons_for_no_streams = video.get('reasonsForNoStreams')
        if reasons_for_no_streams:
            raise ExtractorError(
                '%s returned error: %s' % (self.IE_NAME, '\n'.join(reasons_for_no_streams)),
                expected=True)

        title = video['title']
        description = video.get('description')
        duration = float_or_none(video.get('length'), 1000)
        thumbnail = video.get('posterUrl')

        stream_base_url = video['streamBaseUrl']

        formats = [{
            'url': stream_base_url,
            'play_path': stream['source'],
            'ext': 'flv',
            'tbr': float_or_none(stream.get('bitrate'), 1000),
            'rtmp_real_time': True,
        } for stream in video['streams']]
        self._sort_formats(formats)

        subtitles = {}
        if video.get('hasSubtitle'):
            subtitles = self.extract_subtitles(channel_id, video_id)

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'duration': duration,
            'formats': formats,
            'subtitles': subtitles,
        }
