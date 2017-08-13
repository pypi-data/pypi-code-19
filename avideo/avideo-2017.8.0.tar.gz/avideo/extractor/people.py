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


class PeopleIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?people\.com/people/videos/0,,(?P<id>\d+),00\.html'

    _TEST = {
        'url': 'http://www.people.com/people/videos/0,,20995451,00.html',
        'info_dict': {
            'id': 'ref:20995451',
            'ext': 'mp4',
            'title': 'Astronaut Love Triangle Victim Speaks Out: “The Crime in 2007 Hasn’t Defined Us”',
            'description': 'Colleen Shipman speaks to PEOPLE for the first time about life after the attack',
            'thumbnail': r're:^https?://.*\.jpg',
            'duration': 246.318,
            'timestamp': 1458720585,
            'upload_date': '20160323',
            'uploader_id': '416418724',
        },
        'params': {
            'skip_download': True,
        },
        'add_ie': ['BrightcoveNew'],
    }

    def _real_extract(self, url):
        return self.url_result(
            'http://players.brightcove.net/416418724/default_default/index.html?videoId=ref:%s'
            % self._match_id(url), 'BrightcoveNew')
