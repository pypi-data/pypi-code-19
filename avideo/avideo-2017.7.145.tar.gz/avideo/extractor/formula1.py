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


class Formula1IE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?formula1\.com/(?:content/fom-website/)?en/video/\d{4}/\d{1,2}/(?P<id>.+?)\.html'
    _TESTS = [{
        'url': 'http://www.formula1.com/content/fom-website/en/video/2016/5/Race_highlights_-_Spain_2016.html',
        'md5': '8c79e54be72078b26b89e0e111c0502b',
        'info_dict': {
            'id': 'JvYXJpMzE6pArfHWm5ARp5AiUmD-gibV',
            'ext': 'mp4',
            'title': 'Race highlights - Spain 2016',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        },
        'add_ie': ['Ooyala'],
    }, {
        'url': 'http://www.formula1.com/en/video/2016/5/Race_highlights_-_Spain_2016.html',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        ooyala_embed_code = self._search_regex(
            r'data-videoid="([^"]+)"', webpage, 'ooyala embed code')
        return self.url_result(
            'ooyala:%s' % ooyala_embed_code, 'Ooyala', ooyala_embed_code)
