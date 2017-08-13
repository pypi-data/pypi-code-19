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

from .anvato import AnvatoIE
from .sendtonews import SendtoNewsIE
from ..compat import compat_urlparse
from ..utils import (
    parse_iso8601,
    unified_timestamp,
)


class CBSLocalIE(AnvatoIE):
    _VALID_URL = r'https?://[a-z]+\.cbslocal\.com/(?:\d+/\d+/\d+|video)/(?P<id>[0-9a-z-]+)'

    _TESTS = [{
        # Anvato backend
        'url': 'http://losangeles.cbslocal.com/2016/05/16/safety-advocates-say-fatal-car-seat-failures-are-public-health-crisis',
        'md5': 'f0ee3081e3843f575fccef901199b212',
        'info_dict': {
            'id': '3401037',
            'ext': 'mp4',
            'title': 'Safety Advocates Say Fatal Car Seat Failures Are \'Public Health Crisis\'',
            'description': 'Collapsing seats have been the focus of scrutiny for decades, though experts say remarkably little has been done to address the issue. Randy Paige reports.',
            'thumbnail': 're:^https?://.*',
            'timestamp': 1463440500,
            'upload_date': '20160516',
            'uploader': 'CBS',
            'subtitles': {
                'en': 'mincount:5',
            },
            'categories': [
                'Stations\\Spoken Word\\KCBSTV',
                'Syndication\\MSN',
                'Syndication\\NDN',
                'Syndication\\AOL',
                'Syndication\\Yahoo',
                'Syndication\\Tribune',
                'Syndication\\Curb.tv',
                'Content\\News'
            ],
            'tags': ['CBS 2 News Evening'],
        },
    }, {
        # SendtoNews embed
        'url': 'http://cleveland.cbslocal.com/2016/05/16/indians-score-season-high-15-runs-in-blowout-win-over-reds-rapid-reaction/',
        'info_dict': {
            'id': 'GxfCe0Zo7D-175909-5588',
        },
        'playlist_count': 9,
        'params': {
            # m3u8 download
            'skip_download': True,
        },
    }, {
        'url': 'http://newyork.cbslocal.com/video/3580809-a-very-blue-anniversary/',
        'info_dict': {
            'id': '3580809',
            'ext': 'mp4',
            'title': 'A Very Blue Anniversary',
            'description': 'CBS2’s Cindy Hsu has more.',
            'thumbnail': 're:^https?://.*',
            'timestamp': int,
            'upload_date': r're:^\d{8}$',
            'uploader': 'CBS',
            'subtitles': {
                'en': 'mincount:5',
            },
            'categories': [
                'Stations\\Spoken Word\\WCBSTV',
                'Syndication\\AOL',
                'Syndication\\MSN',
                'Syndication\\NDN',
                'Syndication\\Yahoo',
                'Content\\News',
                'Content\\News\\Local News',
            ],
            'tags': ['CBS 2 News Weekends', 'Cindy Hsu', 'Blue Man Group'],
        },
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        sendtonews_url = SendtoNewsIE._extract_url(webpage)
        if sendtonews_url:
            return self.url_result(
                compat_urlparse.urljoin(url, sendtonews_url),
                ie=SendtoNewsIE.ie_key())

        info_dict = self._extract_anvato_videos(webpage, display_id)

        time_str = self._html_search_regex(
            r'class="entry-date">([^<]+)<', webpage, 'released date', default=None)
        if time_str:
            timestamp = unified_timestamp(time_str)
        else:
            timestamp = parse_iso8601(self._html_search_meta('uploadDate', webpage))

        info_dict.update({
            'display_id': display_id,
            'timestamp': timestamp,
        })

        return info_dict
