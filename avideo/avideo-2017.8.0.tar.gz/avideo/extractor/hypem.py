
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

import json
import time

from .common import InfoExtractor
from ..compat import compat_urllib_parse_urlencode
from ..utils import (
    ExtractorError,
    sanitized_Request,
)


class HypemIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?hypem\.com/track/(?P<id>[^/]+)/'
    _TEST = {
        'url': 'http://hypem.com/track/1v6ga/BODYWORK+-+TAME',
        'md5': 'b9cc91b5af8995e9f0c1cee04c575828',
        'info_dict': {
            'id': '1v6ga',
            'ext': 'mp3',
            'title': 'Tame',
            'uploader': 'BODYWORK',
        }
    }

    def _real_extract(self, url):
        track_id = self._match_id(url)

        data = {'ax': 1, 'ts': time.time()}
        request = sanitized_Request(url + '?' + compat_urllib_parse_urlencode(data))
        response, urlh = self._download_webpage_handle(
            request, track_id, 'Downloading webpage with the url')

        html_tracks = self._html_search_regex(
            r'(?ms)<script type="application/json" id="displayList-data">(.+?)</script>',
            response, 'tracks')
        try:
            track_list = json.loads(html_tracks)
            track = track_list['tracks'][0]
        except ValueError:
            raise ExtractorError('Hypemachine contained invalid JSON.')

        key = track['key']
        track_id = track['id']
        title = track['song']

        request = sanitized_Request(
            'http://hypem.com/serve/source/%s/%s' % (track_id, key),
            '', {'Content-Type': 'application/json'})
        song_data = self._download_json(request, track_id, 'Downloading metadata')
        final_url = song_data['url']
        artist = track.get('artist')

        return {
            'id': track_id,
            'url': final_url,
            'ext': 'mp3',
            'title': title,
            'uploader': artist,
        }
