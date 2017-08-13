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
from ..utils import (
    clean_html,
    get_element_by_class,
    js_to_json,
)


class TVNoeIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?tvnoe\.cz/video/(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://www.tvnoe.cz/video/10362',
        'md5': 'aee983f279aab96ec45ab6e2abb3c2ca',
        'info_dict': {
            'id': '10362',
            'ext': 'mp4',
            'series': 'Noční univerzita',
            'title': 'prof. Tomáš Halík, Th.D. - Návrat náboženství a střet civilizací',
            'description': 'md5:f337bae384e1a531a52c55ebc50fff41',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        iframe_url = self._search_regex(
            r'<iframe[^>]+src="([^"]+)"', webpage, 'iframe URL')

        ifs_page = self._download_webpage(iframe_url, video_id)
        jwplayer_data = self._find_jwplayer_data(
            ifs_page, video_id, transform_source=js_to_json)
        info_dict = self._parse_jwplayer_data(
            jwplayer_data, video_id, require_title=False, base_url=iframe_url)

        info_dict.update({
            'id': video_id,
            'title': clean_html(get_element_by_class(
                'field-name-field-podnazev', webpage)),
            'description': clean_html(get_element_by_class(
                'field-name-body', webpage)),
            'series': clean_html(get_element_by_class('title', webpage))
        })

        return info_dict
