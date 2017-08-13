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
from ..compat import compat_str
from ..utils import (
    int_or_none,
    float_or_none,
    ExtractorError,
)


class NineNowIE(InfoExtractor):
    IE_NAME = '9now.com.au'
    _VALID_URL = r'https?://(?:www\.)?9now\.com\.au/(?:[^/]+/){2}(?P<id>[^/?#]+)'
    _TESTS = [{
        # clip
        'url': 'https://www.9now.com.au/afl-footy-show/2016/clip-ciql02091000g0hp5oktrnytc',
        'md5': '17cf47d63ec9323e562c9957a968b565',
        'info_dict': {
            'id': '16801',
            'ext': 'mp4',
            'title': 'St. Kilda\'s Joey Montagna on the potential for a player\'s strike',
            'description': 'Is a boycott of the NAB Cup "on the table"?',
            'uploader_id': '4460760524001',
            'upload_date': '20160713',
            'timestamp': 1468421266,
        },
        'skip': 'Only available in Australia',
    }, {
        # episode
        'url': 'https://www.9now.com.au/afl-footy-show/2016/episode-19',
        'only_matching': True,
    }, {
        # DRM protected
        'url': 'https://www.9now.com.au/andrew-marrs-history-of-the-world/season-1/episode-1',
        'only_matching': True,
    }]
    BRIGHTCOVE_URL_TEMPLATE = 'http://players.brightcove.net/4460760524001/default_default/index.html?videoId=%s'

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        page_data = self._parse_json(self._search_regex(
            r'window\.__data\s*=\s*({.*?});', webpage,
            'page data'), display_id)

        for kind in ('episode', 'clip'):
            current_key = page_data.get(kind, {}).get(
                'current%sKey' % kind.capitalize())
            if not current_key:
                continue
            cache = page_data.get(kind, {}).get('%sCache' % kind, {})
            if not cache:
                continue
            common_data = (cache.get(current_key) or list(cache.values())[0])[kind]
            break
        else:
            raise ExtractorError('Unable to find video data')

        video_data = common_data['video']

        if video_data.get('drm'):
            raise ExtractorError('This video is DRM protected.', expected=True)

        brightcove_id = video_data.get('brightcoveId') or 'ref:' + video_data['referenceId']
        video_id = compat_str(video_data.get('id') or brightcove_id)
        title = common_data['name']

        thumbnails = [{
            'id': thumbnail_id,
            'url': thumbnail_url,
            'width': int_or_none(thumbnail_id[1:])
        } for thumbnail_id, thumbnail_url in common_data.get('image', {}).get('sizes', {}).items()]

        return {
            '_type': 'url_transparent',
            'url': self.BRIGHTCOVE_URL_TEMPLATE % brightcove_id,
            'id': video_id,
            'title': title,
            'description': common_data.get('description'),
            'duration': float_or_none(video_data.get('duration'), 1000),
            'thumbnails': thumbnails,
            'ie_key': 'BrightcoveNew',
        }
