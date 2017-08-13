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
from ..compat import compat_str
from ..utils import (
    ExtractorError,
    int_or_none,
    parse_iso8601,
)


class PlayFMIE(InfoExtractor):
    IE_NAME = 'play.fm'
    _VALID_URL = r'https?://(?:www\.)?play\.fm/(?P<slug>(?:[^/]+/)+(?P<id>[^/]+))/?(?:$|[?#])'

    _TEST = {
        'url': 'https://www.play.fm/dan-drastic/sven-tasnadi-leipzig-electronic-music-batofar-paris-fr-2014-07-12',
        'md5': 'c505f8307825a245d0c7ad1850001f22',
        'info_dict': {
            'id': '71276',
            'ext': 'mp3',
            'title': 'Sven Tasnadi - LEIPZIG ELECTRONIC MUSIC @ Batofar (Paris,FR) - 2014-07-12',
            'description': '',
            'duration': 5627,
            'timestamp': 1406033781,
            'upload_date': '20140722',
            'uploader': 'Dan Drastic',
            'uploader_id': '71170',
            'view_count': int,
            'comment_count': int,
        },
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        slug = mobj.group('slug')

        recordings = self._download_json(
            'http://v2api.play.fm/recordings/slug/%s' % slug, video_id)

        error = recordings.get('error')
        if isinstance(error, dict):
            raise ExtractorError(
                '%s returned error: %s' % (self.IE_NAME, error.get('message')),
                expected=True)

        audio_url = recordings['audio']
        video_id = compat_str(recordings.get('id') or video_id)
        title = recordings['title']
        description = recordings.get('description')
        duration = int_or_none(recordings.get('recordingDuration'))
        timestamp = parse_iso8601(recordings.get('created_at'))
        uploader = recordings.get('page', {}).get('title')
        uploader_id = compat_str(recordings.get('page', {}).get('id'))
        view_count = int_or_none(recordings.get('playCount'))
        comment_count = int_or_none(recordings.get('commentCount'))
        categories = [tag['name'] for tag in recordings.get('tags', []) if tag.get('name')]

        return {
            'id': video_id,
            'url': audio_url,
            'title': title,
            'description': description,
            'duration': duration,
            'timestamp': timestamp,
            'uploader': uploader,
            'uploader_id': uploader_id,
            'view_count': view_count,
            'comment_count': comment_count,
            'categories': categories,
        }
