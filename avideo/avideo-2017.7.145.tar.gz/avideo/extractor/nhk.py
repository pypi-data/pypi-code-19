
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
from ..utils import ExtractorError


class NhkVodIE(InfoExtractor):
    _VALID_URL = r'https?://www3\.nhk\.or\.jp/nhkworld/en/vod/(?P<id>[^/]+/[^/?#&]+)'
    _TEST = {
        # Videos available only for a limited period of time. Visit
        # http://www3.nhk.or.jp/nhkworld/en/vod/ for working samples.
        'url': 'http://www3.nhk.or.jp/nhkworld/en/vod/tokyofashion/20160815',
        'info_dict': {
            'id': 'A1bnNiNTE6nY3jLllS-BIISfcC_PpvF5',
            'ext': 'flv',
            'title': 'TOKYO FASHION EXPRESS - The Kimono as Global Fashion',
            'description': 'md5:db338ee6ce8204f415b754782f819824',
            'series': 'TOKYO FASHION EXPRESS',
            'episode': 'The Kimono as Global Fashion',
        },
        'skip': 'Videos available only for a limited period of time',
    }
    _API_URL = 'http://api.nhk.or.jp/nhkworld/vodesdlist/v1/all/all/all.json?apikey=EJfK8jdS57GqlupFgAfAAwr573q01y6k'

    def _real_extract(self, url):
        video_id = self._match_id(url)

        data = self._download_json(self._API_URL, video_id)

        try:
            episode = next(
                e for e in data['data']['episodes']
                if e.get('url') and video_id in e['url'])
        except StopIteration:
            raise ExtractorError('Unable to find episode')

        embed_code = episode['vod_id']

        title = episode.get('sub_title_clean') or episode['sub_title']
        description = episode.get('description_clean') or episode.get('description')
        series = episode.get('title_clean') or episode.get('title')

        return {
            '_type': 'url_transparent',
            'ie_key': 'Ooyala',
            'url': 'ooyala:%s' % embed_code,
            'title': '%s - %s' % (series, title) if series and title else title,
            'description': description,
            'series': series,
            'episode': title,
        }
