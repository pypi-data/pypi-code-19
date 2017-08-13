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


class SeekerIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?seeker\.com/(?P<display_id>.*)-(?P<article_id>\d+)\.html'
    _TESTS = [{
        # player.loadRevision3Item
        'url': 'http://www.seeker.com/should-trump-be-required-to-release-his-tax-returns-1833805621.html',
        'md5': '30c1dc4030cc715cf05b423d0947ac18',
        'info_dict': {
            'id': '76243',
            'ext': 'webm',
            'title': 'Should Trump Be Required To Release His Tax Returns?',
            'description': 'Donald Trump has been secretive about his "big," "beautiful" tax returns. So what can we learn if he decides to release them?',
            'uploader': 'Seeker Daily',
            'uploader_id': 'seekerdaily',
        }
    }, {
        'url': 'http://www.seeker.com/changes-expected-at-zoos-following-recent-gorilla-lion-shootings-1834116536.html',
        'playlist': [
            {
                'md5': '83bcd157cab89ad7318dd7b8c9cf1306',
                'info_dict': {
                    'id': '67558',
                    'ext': 'mp4',
                    'title': 'The Pros & Cons Of Zoos',
                    'description': 'Zoos are often depicted as a terrible place for animals to live, but is there any truth to this?',
                    'uploader': 'DNews',
                    'uploader_id': 'dnews',
                },
            }
        ],
        'info_dict': {
            'id': '1834116536',
            'title': 'After Gorilla Killing, Changes Ahead for Zoos',
            'description': 'The largest association of zoos and others are hoping to learn from recent incidents that led to the shooting deaths of a gorilla and two lions.',
        },
    }]

    def _real_extract(self, url):
        display_id, article_id = re.match(self._VALID_URL, url).groups()
        webpage = self._download_webpage(url, display_id)
        mobj = re.search(r"player\.loadRevision3Item\('([^']+)'\s*,\s*(\d+)\);", webpage)
        if mobj:
            playlist_type, playlist_id = mobj.groups()
            return self.url_result(
                'revision3:%s:%s' % (playlist_type, playlist_id), 'Revision3Embed', playlist_id)
        else:
            entries = [self.url_result('revision3:video_id:%s' % video_id, 'Revision3Embed', video_id) for video_id in re.findall(
                r'<iframe[^>]+src=[\'"](?:https?:)?//api\.seekernetwork\.com/player/embed\?videoId=(\d+)', webpage)]
            return self.playlist_result(
                entries, article_id, self._og_search_title(webpage), self._og_search_description(webpage))
