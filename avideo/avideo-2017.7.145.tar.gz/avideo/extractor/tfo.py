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

import json

from .common import InfoExtractor
from ..utils import (
    HEADRequest,
    ExtractorError,
    int_or_none,
    clean_html,
)


class TFOIE(InfoExtractor):
    _GEO_COUNTRIES = ['CA']
    _VALID_URL = r'https?://(?:www\.)?tfo\.org/(?:en|fr)/(?:[^/]+/){2}(?P<id>\d+)'
    _TEST = {
        'url': 'http://www.tfo.org/en/universe/tfo-247/100463871/video-game-hackathon',
        'md5': '47c987d0515561114cf03d1226a9d4c7',
        'info_dict': {
            'id': '100463871',
            'ext': 'mp4',
            'title': 'Video Game Hackathon',
            'description': 'md5:558afeba217c6c8d96c60e5421795c07',
            'upload_date': '20160212',
            'timestamp': 1455310233,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        self._request_webpage(HEADRequest('http://www.tfo.org/'), video_id)
        infos = self._download_json(
            'http://www.tfo.org/api/web/video/get_infos', video_id, data=json.dumps({
                'product_id': video_id,
            }).encode(), headers={
                'X-tfo-session': self._get_cookies('http://www.tfo.org/')['tfo-session'].value,
            })
        if infos.get('success') == 0:
            if infos.get('code') == 'ErrGeoBlocked':
                self.raise_geo_restricted(countries=self._GEO_COUNTRIES)
            raise ExtractorError('%s said: %s' % (self.IE_NAME, clean_html(infos['msg'])), expected=True)
        video_data = infos['data']

        return {
            '_type': 'url_transparent',
            'id': video_id,
            'url': 'limelight:media:' + video_data['llid'],
            'title': video_data['title'],
            'description': video_data.get('description'),
            'series': video_data.get('collection'),
            'season_number': int_or_none(video_data.get('season')),
            'episode_number': int_or_none(video_data.get('episode')),
            'duration': int_or_none(video_data.get('duration')),
            'ie_key': 'LimelightMedia',
        }
