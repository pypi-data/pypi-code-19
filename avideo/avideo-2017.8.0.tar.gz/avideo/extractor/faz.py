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
    xpath_element,
    xpath_text,
    int_or_none,
)


class FazIE(InfoExtractor):
    IE_NAME = 'faz.net'
    _VALID_URL = r'https?://(?:www\.)?faz\.net/(?:[^/]+/)*.*?-(?P<id>\d+)\.html'

    _TESTS = [{
        'url': 'http://www.faz.net/multimedia/videos/stockholm-chemie-nobelpreis-fuer-drei-amerikanische-forscher-12610585.html',
        'info_dict': {
            'id': '12610585',
            'ext': 'mp4',
            'title': 'Stockholm: Chemie-Nobelpreis für drei amerikanische Forscher',
            'description': 'md5:1453fbf9a0d041d985a47306192ea253',
        },
    }, {
        'url': 'http://www.faz.net/aktuell/politik/berlin-gabriel-besteht-zerreissprobe-ueber-datenspeicherung-13659345.html',
        'only_matching': True,
    }, {
        'url': 'http://www.faz.net/berlin-gabriel-besteht-zerreissprobe-ueber-datenspeicherung-13659345.html',
        'only_matching': True,
    }, {
        'url': 'http://www.faz.net/-13659345.html',
        'only_matching': True,
    }, {
        'url': 'http://www.faz.net/aktuell/politik/-13659345.html',
        'only_matching': True,
    }, {
        'url': 'http://www.faz.net/foobarblafasel-13659345.html',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)
        description = self._og_search_description(webpage)
        config_xml_url = self._search_regex(
            r'videoXMLURL\s*=\s*"([^"]+)', webpage, 'config xml url')
        config = self._download_xml(
            config_xml_url, video_id, 'Downloading config xml')

        encodings = xpath_element(config, 'ENCODINGS', 'encodings', True)
        formats = []
        for pref, code in enumerate(['LOW', 'HIGH', 'HQ']):
            encoding = xpath_element(encodings, code)
            if encoding is not None:
                encoding_url = xpath_text(encoding, 'FILENAME')
                if encoding_url:
                    formats.append({
                        'url': encoding_url,
                        'format_id': code.lower(),
                        'quality': pref,
                        'tbr': int_or_none(xpath_text(encoding, 'AVERAGEBITRATE')),
                    })
        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': self._og_search_title(webpage),
            'formats': formats,
            'description': description.strip() if description else None,
            'thumbnail': xpath_text(config, 'STILL/STILL_BIG'),
            'duration': int_or_none(xpath_text(config, 'DURATION')),
        }
