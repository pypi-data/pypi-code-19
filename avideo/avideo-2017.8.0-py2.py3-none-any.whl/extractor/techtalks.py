
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
from ..utils import (
    get_element_by_attribute,
    clean_html,
)


class TechTalksIE(InfoExtractor):
    _VALID_URL = r'https?://techtalks\.tv/talks/(?:[^/]+/)?(?P<id>\d+)'

    _TESTS = [{
        'url': 'http://techtalks.tv/talks/learning-topic-models-going-beyond-svd/57758/',
        'info_dict': {
            'id': '57758',
            'title': 'Learning Topic Models --- Going beyond SVD',
        },
        'playlist': [
            {
                'info_dict': {
                    'id': '57758',
                    'ext': 'flv',
                    'title': 'Learning Topic Models --- Going beyond SVD',
                },
            },
            {
                'info_dict': {
                    'id': '57758-slides',
                    'ext': 'flv',
                    'title': 'Learning Topic Models --- Going beyond SVD',
                },
            },
        ],
        'params': {
            # rtmp download
            'skip_download': True,
        },
    }, {
        'url': 'http://techtalks.tv/talks/57758',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        talk_id = mobj.group('id')
        webpage = self._download_webpage(url, talk_id)
        rtmp_url = self._search_regex(
            r'netConnectionUrl: \'(.*?)\'', webpage, 'rtmp url')
        play_path = self._search_regex(
            r'href=\'(.*?)\' [^>]*id="flowplayer_presenter"',
            webpage, 'presenter play path')
        title = clean_html(get_element_by_attribute('class', 'title', webpage))
        video_info = {
            'id': talk_id,
            'title': title,
            'url': rtmp_url,
            'play_path': play_path,
            'ext': 'flv',
        }
        m_slides = re.search(r'<a class="slides" href=\'(.*?)\'', webpage)
        if m_slides is None:
            return video_info
        else:
            return {
                '_type': 'playlist',
                'id': talk_id,
                'title': title,
                'entries': [
                    video_info,
                    # The slides video
                    {
                        'id': talk_id + '-slides',
                        'title': title,
                        'url': rtmp_url,
                        'play_path': m_slides.group(1),
                        'ext': 'flv',
                    },
                ],
            }
