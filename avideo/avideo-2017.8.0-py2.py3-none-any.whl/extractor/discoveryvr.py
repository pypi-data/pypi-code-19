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
from ..utils import parse_duration


class DiscoveryVRIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?discoveryvr\.com/watch/(?P<id>[^/?#]+)'
    _TEST = {
        'url': 'http://www.discoveryvr.com/watch/discovery-vr-an-introduction',
        'md5': '32b1929798c464a54356378b7912eca4',
        'info_dict': {
            'id': 'discovery-vr-an-introduction',
            'ext': 'mp4',
            'title': 'Discovery VR - An Introduction',
            'description': 'md5:80d418a10efb8899d9403e61d8790f06',
        }
    }

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        bootstrap_data = self._search_regex(
            r'root\.DVR\.bootstrapData\s+=\s+"({.+?})";',
            webpage, 'bootstrap data')
        bootstrap_data = self._parse_json(
            bootstrap_data.encode('utf-8').decode('unicode_escape'),
            display_id)
        videos = self._parse_json(bootstrap_data['videos'], display_id)['allVideos']
        video_data = next(video for video in videos if video.get('slug') == display_id)

        series = video_data.get('showTitle')
        title = episode = video_data.get('title') or series
        if series and series != title:
            title = '%s - %s' % (series, title)

        formats = []
        for f, format_id in (('cdnUriM3U8', 'mobi'), ('webVideoUrlSd', 'sd'), ('webVideoUrlHd', 'hd')):
            f_url = video_data.get(f)
            if not f_url:
                continue
            formats.append({
                'format_id': format_id,
                'url': f_url,
            })

        return {
            'id': display_id,
            'display_id': display_id,
            'title': title,
            'description': video_data.get('description'),
            'thumbnail': video_data.get('thumbnail'),
            'duration': parse_duration(video_data.get('runTime')),
            'formats': formats,
            'episode': episode,
            'series': series,
        }
