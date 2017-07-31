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


class LocalNews8IE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?localnews8\.com/(?:[^/]+/)*(?P<display_id>[^/]+)/(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://www.localnews8.com/news/rexburg-business-turns-carbon-fiber-scraps-into-wedding-rings/35183304',
        'md5': 'be4d48aea61aa2bde7be2ee47691ad20',
        'info_dict': {
            'id': '35183304',
            'display_id': 'rexburg-business-turns-carbon-fiber-scraps-into-wedding-rings',
            'ext': 'mp4',
            'title': 'Rexburg business turns carbon fiber scraps into wedding ring',
            'description': 'The process was first invented by Lamborghini and less than a dozen companies around the world use it.',
            'duration': 153,
            'timestamp': 1441844822,
            'upload_date': '20150910',
            'uploader_id': 'api',
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        display_id = mobj.group('display_id')

        webpage = self._download_webpage(url, display_id)

        partner_id = self._search_regex(
            r'partnerId\s*[:=]\s*(["\'])(?P<id>\d+)\1',
            webpage, 'partner id', group='id')
        kaltura_id = self._search_regex(
            r'videoIdString\s*[:=]\s*(["\'])kaltura:(?P<id>[0-9a-z_]+)\1',
            webpage, 'videl id', group='id')

        return {
            '_type': 'url_transparent',
            'url': 'kaltura:%s:%s' % (partner_id, kaltura_id),
            'ie_key': 'Kaltura',
            'id': video_id,
            'display_id': display_id,
        }
