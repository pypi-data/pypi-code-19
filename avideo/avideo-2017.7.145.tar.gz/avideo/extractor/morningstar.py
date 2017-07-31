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


class MorningstarIE(InfoExtractor):
    IE_DESC = 'morningstar.com'
    _VALID_URL = r'https?://(?:www\.)?morningstar\.com/[cC]over/video[cC]enter\.aspx\?id=(?P<id>[0-9]+)'
    _TEST = {
        'url': 'http://www.morningstar.com/cover/videocenter.aspx?id=615869',
        'md5': '6c0acface7a787aadc8391e4bbf7b0f5',
        'info_dict': {
            'id': '615869',
            'ext': 'mp4',
            'title': 'Get Ahead of the Curve on 2013 Taxes',
            'description': "Vanguard's Joel Dickson on managing higher tax rates for high-income earners and fund capital-gain distributions in 2013.",
            'thumbnail': r're:^https?://.*m(?:orning)?star\.com/.+thumb\.jpg$'
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')

        webpage = self._download_webpage(url, video_id)
        title = self._html_search_regex(
            r'<h1 id="titleLink">(.*?)</h1>', webpage, 'title')
        video_url = self._html_search_regex(
            r'<input type="hidden" id="hidVideoUrl" value="([^"]+)"',
            webpage, 'video URL')
        thumbnail = self._html_search_regex(
            r'<input type="hidden" id="hidSnapshot" value="([^"]+)"',
            webpage, 'thumbnail', fatal=False)
        description = self._html_search_regex(
            r'<div id="mstarDeck".*?>(.*?)</div>',
            webpage, 'description', fatal=False)

        return {
            'id': video_id,
            'title': title,
            'url': video_url,
            'thumbnail': thumbnail,
            'description': description,
        }
