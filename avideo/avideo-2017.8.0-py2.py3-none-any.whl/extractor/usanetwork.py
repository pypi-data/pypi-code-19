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

from .adobepass import AdobePassIE
from ..utils import (
    extract_attributes,
    smuggle_url,
    update_url_query,
)


class USANetworkIE(AdobePassIE):
    _VALID_URL = r'https?://(?:www\.)?usanetwork\.com/(?:[^/]+/videos|movies)/(?P<id>[^/?#]+)'
    _TEST = {
        'url': 'http://www.usanetwork.com/mrrobot/videos/hpe-cybersecurity',
        'md5': '33c0d2ba381571b414024440d08d57fd',
        'info_dict': {
            'id': '3086229',
            'ext': 'mp4',
            'title': 'HPE Cybersecurity',
            'description': 'The more we digitize our world, the more vulnerable we are.',
            'upload_date': '20160818',
            'timestamp': 1471535460,
            'uploader': 'NBCU-USA',
        },
    }

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        player_params = extract_attributes(self._search_regex(
            r'(<div[^>]+data-usa-tve-player-container[^>]*>)', webpage, 'player params'))
        video_id = player_params['data-mpx-guid']
        title = player_params['data-episode-title']

        account_pid, path = re.search(
            r'data-src="(?:https?)?//player\.theplatform\.com/p/([^/]+)/.*?/(media/guid/\d+/\d+)',
            webpage).groups()

        query = {
            'mbr': 'true',
        }
        if player_params.get('data-is-full-episode') == '1':
            query['manifest'] = 'm3u'

        if player_params.get('data-entitlement') == 'auth':
            adobe_pass = {}
            drupal_settings = self._search_regex(
                r'jQuery\.extend\(Drupal\.settings\s*,\s*({.+?})\);',
                webpage, 'drupal settings', fatal=False)
            if drupal_settings:
                drupal_settings = self._parse_json(drupal_settings, video_id, fatal=False)
                if drupal_settings:
                    adobe_pass = drupal_settings.get('adobePass', {})
            resource = self._get_mvpd_resource(
                adobe_pass.get('adobePassResourceId', 'usa'),
                title, video_id, player_params.get('data-episode-rating', 'TV-14'))
            query['auth'] = self._extract_mvpd_auth(
                url, video_id, adobe_pass.get('adobePassRequestorId', 'usa'), resource)

        info = self._search_json_ld(webpage, video_id, default={})
        info.update({
            '_type': 'url_transparent',
            'url': smuggle_url(update_url_query(
                'http://link.theplatform.com/s/%s/%s' % (account_pid, path),
                query), {'force_smil_url': True}),
            'id': video_id,
            'title': title,
            'series': player_params.get('data-show-title'),
            'episode': title,
            'ie_key': 'ThePlatform',
        })
        return info
