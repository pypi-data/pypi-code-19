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


class RestudyIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?restudy\.dk/video/play/id/(?P<id>[0-9]+)'
    _TEST = {
        'url': 'https://www.restudy.dk/video/play/id/1637',
        'info_dict': {
            'id': '1637',
            'ext': 'flv',
            'title': 'Leiden-frosteffekt',
            'description': 'Denne video er et eksperiment med flydende kvælstof.',
        },
        'params': {
            # rtmp download
            'skip_download': True,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        title = self._og_search_title(webpage).strip()
        description = self._og_search_description(webpage).strip()

        formats = self._extract_smil_formats(
            'https://www.restudy.dk/awsmedia/SmilDirectory/video_%s.xml' % video_id,
            video_id)
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'formats': formats,
        }
