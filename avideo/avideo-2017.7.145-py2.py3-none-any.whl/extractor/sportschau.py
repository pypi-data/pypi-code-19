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

from .wdr import WDRBaseIE
from ..utils import get_element_by_attribute


class SportschauIE(WDRBaseIE):
    IE_NAME = 'Sportschau'
    _VALID_URL = r'https?://(?:www\.)?sportschau\.de/(?:[^/]+/)+video-?(?P<id>[^/#?]+)\.html'
    _TEST = {
        'url': 'http://www.sportschau.de/uefaeuro2016/videos/video-dfb-team-geht-gut-gelaunt-ins-spiel-gegen-polen-100.html',
        'info_dict': {
            'id': 'mdb-1140188',
            'display_id': 'dfb-team-geht-gut-gelaunt-ins-spiel-gegen-polen-100',
            'ext': 'mp4',
            'title': 'DFB-Team geht gut gelaunt ins Spiel gegen Polen',
            'description': 'Vor dem zweiten Gruppenspiel gegen Polen herrscht gute Stimmung im deutschen Team. Insbesondere Bastian Schweinsteiger strotzt vor Optimismus nach seinem Tor gegen die Ukraine.',
            'upload_date': '20160615',
        },
        'skip': 'Geo-restricted to Germany',
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)
        title = get_element_by_attribute('class', 'headline', webpage)
        description = self._html_search_meta('description', webpage, 'description')

        info = self._extract_wdr_video(webpage, video_id)

        info.update({
            'title': title,
            'description': description,
        })

        return info
