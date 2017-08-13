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

from .ard import ARDMediathekIE
from ..utils import (
    ExtractorError,
    get_element_by_attribute,
)


class SRMediathekIE(ARDMediathekIE):
    IE_NAME = 'sr:mediathek'
    IE_DESC = 'Saarländischer Rundfunk'
    _VALID_URL = r'https?://sr-mediathek(?:\.sr-online)?\.de/index\.php\?.*?&id=(?P<id>[0-9]+)'

    _TESTS = [{
        'url': 'http://sr-mediathek.sr-online.de/index.php?seite=7&id=28455',
        'info_dict': {
            'id': '28455',
            'ext': 'mp4',
            'title': 'sportarena (26.10.2014)',
            'description': 'Ringen: KSV Köllerbach gegen Aachen-Walheim; Frauen-Fußball: 1. FC Saarbrücken gegen Sindelfingen; Motorsport: Rallye in Losheim; dazu: Interview mit Timo Bernhard; Turnen: TG Saar; Reitsport: Deutscher Voltigier-Pokal; Badminton: Interview mit Michael Fuchs ',
            'thumbnail': r're:^https?://.*\.jpg$',
        },
        'skip': 'no longer available',
    }, {
        'url': 'http://sr-mediathek.sr-online.de/index.php?seite=7&id=37682',
        'info_dict': {
            'id': '37682',
            'ext': 'mp4',
            'title': 'Love, Cakes and Rock\'n\'Roll',
            'description': 'md5:18bf9763631c7d326c22603681e1123d',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
    }, {
        'url': 'http://sr-mediathek.de/index.php?seite=7&id=7480',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        if '>Der gew&uuml;nschte Beitrag ist leider nicht mehr verf&uuml;gbar.<' in webpage:
            raise ExtractorError('Video %s is no longer available' % video_id, expected=True)

        media_collection_url = self._search_regex(
            r'data-mediacollection-ardplayer="([^"]+)"', webpage, 'media collection url')
        info = self._extract_media_info(media_collection_url, webpage, video_id)
        info.update({
            'id': video_id,
            'title': get_element_by_attribute('class', 'ardplayer-title', webpage),
            'description': self._og_search_description(webpage),
            'thumbnail': self._og_search_thumbnail(webpage),
        })
        return info
