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


class BIQLEIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?biqle\.(?:com|org|ru)/watch/(?P<id>-?\d+_\d+)'
    _TESTS = [{
        'url': 'http://www.biqle.ru/watch/847655_160197695',
        'md5': 'ad5f746a874ccded7b8f211aeea96637',
        'info_dict': {
            'id': '160197695',
            'ext': 'mp4',
            'title': 'Foo Fighters - The Pretender (Live at Wembley Stadium)',
            'uploader': 'Andrey Rogozin',
            'upload_date': '20110605',
        }
    }, {
        'url': 'https://biqle.org/watch/-44781847_168547604',
        'md5': '7f24e72af1db0edf7c1aaba513174f97',
        'info_dict': {
            'id': '168547604',
            'ext': 'mp4',
            'title': 'Ребенок в шоке от автоматической мойки',
            'uploader': 'Dmitry Kotov',
        },
        'skip': ' This video was marked as adult.  Embedding adult videos on external sites is prohibited.',
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        embed_url = self._proto_relative_url(self._search_regex(
            r'<iframe.+?src="((?:http:)?//daxab\.com/[^"]+)".*?></iframe>', webpage, 'embed url'))

        return {
            '_type': 'url_transparent',
            'url': embed_url,
        }
