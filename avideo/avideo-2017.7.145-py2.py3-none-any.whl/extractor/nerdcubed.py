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

import datetime

from .common import InfoExtractor


class NerdCubedFeedIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?nerdcubed\.co\.uk/feed\.json'
    _TEST = {
        'url': 'http://www.nerdcubed.co.uk/feed.json',
        'info_dict': {
            'id': 'nerdcubed-feed',
            'title': 'nerdcubed.co.uk feed',
        },
        'playlist_mincount': 1300,
    }

    def _real_extract(self, url):
        feed = self._download_json(url, url, 'Downloading NerdCubed JSON feed')

        entries = [{
            '_type': 'url',
            'title': feed_entry['title'],
            'uploader': feed_entry['source']['name'] if feed_entry['source'] else None,
            'upload_date': datetime.datetime.strptime(feed_entry['date'], '%Y-%m-%d').strftime('%Y%m%d'),
            'url': 'http://www.youtube.com/watch?v=' + feed_entry['youtube_id'],
        } for feed_entry in feed]

        return {
            '_type': 'playlist',
            'title': 'nerdcubed.co.uk feed',
            'id': 'nerdcubed-feed',
            'entries': entries,
        }
