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


class MakersChannelIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?makerschannel\.com/.*(?P<id_type>video|production)_id=(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://makerschannel.com/en/zoomin/community-highlights?video_id=849',
        'md5': '624a512c6969236b5967bf9286345ad1',
        'info_dict': {
            'id': '849',
            'ext': 'mp4',
            'title': 'Landing a bus on a plane is an epic win',
            'uploader': 'ZoomIn',
            'description': 'md5:cd9cca2ea7b69b78be81d07020c97139',
        }
    }

    def _real_extract(self, url):
        id_type, url_id = re.match(self._VALID_URL, url).groups()
        webpage = self._download_webpage(url, url_id)
        video_data = self._html_search_regex(r'<div([^>]+data-%s-id="%s"[^>]+)>' % (id_type, url_id), webpage, 'video data')

        def extract_data_val(attr, fatal=False):
            return self._html_search_regex(r'data-%s\s*=\s*"([^"]+)"' % attr, video_data, attr, fatal=fatal)
        minoto_id = self._search_regex(r'/id/([a-zA-Z0-9]+)', extract_data_val('video-src', True), 'minoto id')

        return {
            '_type': 'url_transparent',
            'url': 'minoto:%s' % minoto_id,
            'id': extract_data_val('video-id', True),
            'title': extract_data_val('title', True),
            'description': extract_data_val('description'),
            'thumbnail': extract_data_val('image'),
            'uploader': extract_data_val('channel'),
        }
