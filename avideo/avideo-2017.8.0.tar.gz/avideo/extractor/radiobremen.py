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

import re

from .common import InfoExtractor
from ..utils import parse_duration


class RadioBremenIE(InfoExtractor):
    _VALID_URL = r'http?://(?:www\.)?radiobremen\.de/mediathek/(?:index\.html)?\?id=(?P<id>[0-9]+)'
    IE_NAME = 'radiobremen'

    _TEST = {
        'url': 'http://www.radiobremen.de/mediathek/?id=141876',
        'info_dict': {
            'id': '141876',
            'ext': 'mp4',
            'duration': 178,
            'width': 512,
            'title': 'Druck auf Patrick Öztürk',
            'thumbnail': r're:https?://.*\.jpg$',
            'description': 'Gegen den SPD-Bürgerschaftsabgeordneten Patrick Öztürk wird wegen Beihilfe zum gewerbsmäßigen Betrug ermittelt. Am Donnerstagabend sollte er dem Vorstand des SPD-Unterbezirks Bremerhaven dazu Rede und Antwort stehen.',
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        meta_url = 'http://www.radiobremen.de/apps/php/mediathek/metadaten.php?id=%s' % video_id
        meta_doc = self._download_webpage(
            meta_url, video_id, 'Downloading metadata')
        title = self._html_search_regex(
            r'<h1.*>(?P<title>.+)</h1>', meta_doc, 'title')
        description = self._html_search_regex(
            r'<p>(?P<description>.*)</p>', meta_doc, 'description', fatal=False)
        duration = parse_duration(self._html_search_regex(
            r'L&auml;nge:</td>\s+<td>(?P<duration>[0-9]+:[0-9]+)</td>',
            meta_doc, 'duration', fatal=False))

        page_doc = self._download_webpage(
            url, video_id, 'Downloading video information')
        mobj = re.search(
            r"ardformatplayerclassic\(\'playerbereich\',\'(?P<width>[0-9]+)\',\'.*\',\'(?P<video_id>[0-9]+)\',\'(?P<secret>[0-9]+)\',\'(?P<thumbnail>.+)\',\'\'\)",
            page_doc)
        video_url = (
            "http://dl-ondemand.radiobremen.de/mediabase/%s/%s_%s_%s.mp4" %
            (video_id, video_id, mobj.group("secret"), mobj.group('width')))

        formats = [{
            'url': video_url,
            'ext': 'mp4',
            'width': int(mobj.group('width')),
        }]
        return {
            'id': video_id,
            'title': title,
            'description': description,
            'duration': duration,
            'formats': formats,
            'thumbnail': mobj.group('thumbnail'),
        }
