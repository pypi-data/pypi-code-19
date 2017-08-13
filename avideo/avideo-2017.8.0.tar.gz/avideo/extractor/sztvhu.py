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


class SztvHuIE(InfoExtractor):
    _VALID_URL = r'https?://(?:(?:www\.)?sztv\.hu|www\.tvszombathely\.hu)/(?:[^/]+)/.+-(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://sztv.hu/hirek/cserkeszek-nepszerusitettek-a-kornyezettudatos-eletmodot-a-savaria-teren-20130909',
        'md5': 'a6df607b11fb07d0e9f2ad94613375cb',
        'info_dict': {
            'id': '20130909',
            'ext': 'mp4',
            'title': 'Cserkészek népszerűsítették a környezettudatos életmódot a Savaria téren',
            'description': 'A zöld nap játékos ismeretterjesztő programjait a Magyar Cserkész Szövetség szervezte, akik az ország nyolc városában adják át tudásukat az érdeklődőknek. A PET...',
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        video_file = self._search_regex(
            r'file: "...:(.*?)",', webpage, 'video file')
        title = self._html_search_regex(
            r'<meta name="title" content="([^"]*?) - [^-]*? - [^-]*?"',
            webpage, 'video title')
        description = self._html_search_regex(
            r'<meta name="description" content="([^"]*)"/>',
            webpage, 'video description', fatal=False)
        thumbnail = self._og_search_thumbnail(webpage)

        video_url = 'http://media.sztv.hu/vod/' + video_file

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
        }
