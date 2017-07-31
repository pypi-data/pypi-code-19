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


class HGTVComShowIE(InfoExtractor):
    IE_NAME = 'hgtv.com:show'
    _VALID_URL = r'https?://(?:www\.)?hgtv\.com/shows/[^/]+/(?P<id>[^/?#&]+)'
    _TESTS = [{
        # data-module="video"
        'url': 'http://www.hgtv.com/shows/flip-or-flop/flip-or-flop-full-episodes-season-4-videos',
        'info_dict': {
            'id': 'flip-or-flop-full-episodes-season-4-videos',
            'title': 'Flip or Flop Full Episodes',
        },
        'playlist_mincount': 15,
    }, {
        # data-deferred-module="video"
        'url': 'http://www.hgtv.com/shows/good-bones/episodes/an-old-victorian-house-gets-a-new-facelift',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)

        webpage = self._download_webpage(url, display_id)

        config = self._parse_json(
            self._search_regex(
                r'(?s)data-(?:deferred-)?module=["\']video["\'][^>]*>.*?<script[^>]+type=["\']text/x-config["\'][^>]*>(.+?)</script',
                webpage, 'video config'),
            display_id)['channels'][0]

        entries = [
            self.url_result(video['releaseUrl'])
            for video in config['videos'] if video.get('releaseUrl')]

        return self.playlist_result(
            entries, display_id, config.get('title'), config.get('description'))
