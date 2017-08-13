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
from ..compat import (
    compat_HTTPError,
    compat_str,
)
from ..utils import (
    extract_attributes,
    try_get,
    urlencode_postdata,
    ExtractorError,
)


class TVPlayerIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?tvplayer\.com/watch/(?P<id>[^/?#]+)'
    _TEST = {
        'url': 'http://tvplayer.com/watch/bbcone',
        'info_dict': {
            'id': '89',
            'ext': 'mp4',
            'title': r're:^BBC One [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        }
    }

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        current_channel = extract_attributes(self._search_regex(
            r'(<div[^>]+class="[^"]*current-channel[^"]*"[^>]*>)',
            webpage, 'channel element'))
        title = current_channel['data-name']

        resource_id = current_channel['data-id']

        token = self._search_regex(
            r'data-token=(["\'])(?P<token>(?!\1).+)\1', webpage,
            'token', group='token')

        context = self._download_json(
            'https://tvplayer.com/watch/context', display_id,
            'Downloading JSON context', query={
                'resource': resource_id,
                'gen': token,
            })

        validate = context['validate']
        platform = try_get(
            context, lambda x: x['platform']['key'], compat_str) or 'firefox'

        try:
            response = self._download_json(
                'http://api.tvplayer.com/api/v2/stream/live',
                display_id, 'Downloading JSON stream', headers={
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                }, data=urlencode_postdata({
                    'id': resource_id,
                    'service': 1,
                    'platform': platform,
                    'validate': validate,
                }))['tvplayer']['response']
        except ExtractorError as e:
            if isinstance(e.cause, compat_HTTPError):
                response = self._parse_json(
                    e.cause.read().decode(), resource_id)['tvplayer']['response']
                raise ExtractorError(
                    '%s said: %s' % (self.IE_NAME, response['error']), expected=True)
            raise

        formats = self._extract_m3u8_formats(response['stream'], display_id, 'mp4')
        self._sort_formats(formats)

        return {
            'id': resource_id,
            'display_id': display_id,
            'title': self._live_title(title),
            'formats': formats,
            'is_live': True,
        }
