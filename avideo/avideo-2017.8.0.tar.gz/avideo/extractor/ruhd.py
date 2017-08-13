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


class RUHDIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?ruhd\.ru/play\.php\?vid=(?P<id>\d+)'
    _TEST = {
        'url': 'http://www.ruhd.ru/play.php?vid=207',
        'md5': 'd1a9ec4edf8598e3fbd92bb16072ba83',
        'info_dict': {
            'id': '207',
            'ext': 'divx',
            'title': 'КОТ бааааам',
            'description': 'классный кот)',
            'thumbnail': r're:^http://.*\.jpg$',
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        video_url = self._html_search_regex(
            r'<param name="src" value="([^"]+)"', webpage, 'video url')
        title = self._html_search_regex(
            r'<title>([^<]+)&nbsp;&nbsp; RUHD.ru - Видео Высокого качества №1 в России!</title>',
            webpage, 'title')
        description = self._html_search_regex(
            r'(?s)<div id="longdesc">(.+?)<span id="showlink">',
            webpage, 'description', fatal=False)
        thumbnail = self._html_search_regex(
            r'<param name="previewImage" value="([^"]+)"',
            webpage, 'thumbnail', fatal=False)
        if thumbnail:
            thumbnail = 'http://www.ruhd.ru' + thumbnail

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
        }
