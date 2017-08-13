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
from ..utils import (
    determine_ext,
    unescapeHTML,
)


class CJSWIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?cjsw\.com/program/(?P<program>[^/]+)/episode/(?P<id>\d+)'
    _TESTS = [{
        'url': 'http://cjsw.com/program/freshly-squeezed/episode/20170620',
        'md5': 'cee14d40f1e9433632c56e3d14977120',
        'info_dict': {
            'id': '91d9f016-a2e7-46c5-8dcb-7cbcd7437c41',
            'ext': 'mp3',
            'title': 'Freshly Squeezed – Episode June 20, 2017',
            'description': 'md5:c967d63366c3898a80d0c7b0ff337202',
            'series': 'Freshly Squeezed',
            'episode_id': '20170620',
        },
    }, {
        # no description
        'url': 'http://cjsw.com/program/road-pops/episode/20170707/',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        program, episode_id = mobj.group('program', 'id')
        audio_id = '%s/%s' % (program, episode_id)

        webpage = self._download_webpage(url, episode_id)

        title = unescapeHTML(self._search_regex(
            (r'<h1[^>]+class=["\']episode-header__title["\'][^>]*>(?P<title>[^<]+)',
             r'data-audio-title=(["\'])(?P<title>(?:(?!\1).)+)\1'),
            webpage, 'title', group='title'))

        audio_url = self._search_regex(
            r'<button[^>]+data-audio-src=(["\'])(?P<url>(?:(?!\1).)+)\1',
            webpage, 'audio url', group='url')

        audio_id = self._search_regex(
            r'/([\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12})\.mp3',
            audio_url, 'audio id', default=audio_id)

        formats = [{
            'url': audio_url,
            'ext': determine_ext(audio_url, 'mp3'),
            'vcodec': 'none',
        }]

        description = self._html_search_regex(
            r'<p>(?P<description>.+?)</p>', webpage, 'description',
            default=None)
        series = self._search_regex(
            r'data-showname=(["\'])(?P<name>(?:(?!\1).)+)\1', webpage,
            'series', default=program, group='name')

        return {
            'id': audio_id,
            'title': title,
            'description': description,
            'formats': formats,
            'series': series,
            'episode_id': episode_id,
        }
