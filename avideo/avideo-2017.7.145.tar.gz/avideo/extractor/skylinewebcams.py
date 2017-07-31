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


class SkylineWebcamsIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?skylinewebcams\.com/[^/]+/webcam/(?:[^/]+/)+(?P<id>[^/]+)\.html'
    _TEST = {
        'url': 'https://www.skylinewebcams.com/it/webcam/italia/lazio/roma/scalinata-piazza-di-spagna-barcaccia.html',
        'info_dict': {
            'id': 'scalinata-piazza-di-spagna-barcaccia',
            'ext': 'mp4',
            'title': 're:^Live Webcam Scalinata di Piazza di Spagna - La Barcaccia [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$',
            'description': 'Roma, veduta sulla Scalinata di Piazza di Spagna e sulla Barcaccia',
            'is_live': True,
        },
        'params': {
            'skip_download': True,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        stream_url = self._search_regex(
            r'url\s*:\s*(["\'])(?P<url>(?:https?:)?//.+?\.m3u8.*?)\1', webpage,
            'stream url', group='url')

        title = self._og_search_title(webpage)
        description = self._og_search_description(webpage)

        return {
            'id': video_id,
            'url': stream_url,
            'ext': 'mp4',
            'title': self._live_title(title),
            'description': description,
            'is_live': True,
        }
