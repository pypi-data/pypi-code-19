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
from ..compat import compat_urlparse


class FczenitIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?fc-zenit\.ru/video/(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://fc-zenit.ru/video/41044/',
        'md5': '0e3fab421b455e970fa1aa3891e57df0',
        'info_dict': {
            'id': '41044',
            'ext': 'mp4',
            'title': 'Так пишется история: казанский разгром ЦСКА на «Зенит-ТВ»',
        },
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        video_title = self._html_search_regex(
            r'<[^>]+class=\"photoalbum__title\">([^<]+)', webpage, 'title')

        video_items = self._parse_json(self._search_regex(
            r'arrPath\s*=\s*JSON\.parse\(\'(.+)\'\)', webpage, 'video items'),
            video_id)

        def merge_dicts(*dicts):
            ret = {}
            for a_dict in dicts:
                ret.update(a_dict)
            return ret

        formats = [{
            'url': compat_urlparse.urljoin(url, video_url),
            'tbr': int(tbr),
        } for tbr, video_url in merge_dicts(*video_items).items()]

        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': video_title,
            'formats': formats,
        }
