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


class CriterionIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?criterion\.com/films/(?P<id>[0-9]+)-.+'
    _TEST = {
        'url': 'http://www.criterion.com/films/184-le-samourai',
        'md5': 'bc51beba55685509883a9a7830919ec3',
        'info_dict': {
            'id': '184',
            'ext': 'mp4',
            'title': 'Le Samouraï',
            'description': 'md5:a2b4b116326558149bef81f76dcbb93f',
            'thumbnail': r're:^https?://.*\.jpg$',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        final_url = self._search_regex(
            r'so\.addVariable\("videoURL", "(.+?)"\)\;', webpage, 'video url')
        title = self._og_search_title(webpage)
        description = self._html_search_meta('description', webpage)
        thumbnail = self._search_regex(
            r'so\.addVariable\("thumbnailURL", "(.+?)"\)\;',
            webpage, 'thumbnail url')

        return {
            'id': video_id,
            'url': final_url,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
        }
