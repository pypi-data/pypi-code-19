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

from .mtv import MTVServicesInfoExtractor


class TVLandIE(MTVServicesInfoExtractor):
    IE_NAME = 'tvland.com'
    _VALID_URL = r'https?://(?:www\.)?tvland\.com/(?:video-clips|(?:full-)?episodes)/(?P<id>[^/?#.]+)'
    _FEED_URL = 'http://www.tvland.com/feeds/mrss/'
    _TESTS = [{
        # Geo-restricted. Without a proxy metadata are still there. With a
        # proxy it redirects to http://m.tvland.com/app/
        'url': 'http://www.tvland.com/episodes/hqhps2/everybody-loves-raymond-the-invasion-ep-048',
        'info_dict': {
            'description': 'md5:80973e81b916a324e05c14a3fb506d29',
            'title': 'The Invasion',
        },
        'playlist': [],
    }, {
        'url': 'http://www.tvland.com/video-clips/zea2ev/younger-younger--hilary-duff---little-lies',
        'md5': 'e2c6389401cf485df26c79c247b08713',
        'info_dict': {
            'id': 'b8697515-4bbe-4e01-83d5-fa705ce5fa88',
            'ext': 'mp4',
            'title': 'Younger|December 28, 2015|2|NO-EPISODE#|Younger: Hilary Duff - Little Lies',
            'description': 'md5:7d192f56ca8d958645c83f0de8ef0269',
            'upload_date': '20151228',
            'timestamp': 1451289600,
        },
    }, {
        'url': 'http://www.tvland.com/full-episodes/iu0hz6/younger-a-kiss-is-just-a-kiss-season-3-ep-301',
        'only_matching': True,
    }]
