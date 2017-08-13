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
from ..utils import unescapeHTML


class BaiduVideoIE(InfoExtractor):
    IE_DESC = '百度视频'
    _VALID_URL = r'https?://v\.baidu\.com/(?P<type>[a-z]+)/(?P<id>\d+)\.htm'
    _TESTS = [{
        'url': 'http://v.baidu.com/comic/1069.htm?frp=bdbrand&q=%E4%B8%AD%E5%8D%8E%E5%B0%8F%E5%BD%93%E5%AE%B6',
        'info_dict': {
            'id': '1069',
            'title': '中华小当家 TV版国语',
            'description': 'md5:51be07afe461cf99fa61231421b5397c',
        },
        'playlist_count': 52,
    }, {
        'url': 'http://v.baidu.com/show/11595.htm?frp=bdbrand',
        'info_dict': {
            'id': '11595',
            'title': 're:^奔跑吧兄弟',
            'description': 'md5:1bf88bad6d850930f542d51547c089b8',
        },
        'playlist_mincount': 12,
    }]

    def _call_api(self, path, category, playlist_id, note):
        return self._download_json('http://app.video.baidu.com/%s/?worktype=adnative%s&id=%s' % (
            path, category, playlist_id), playlist_id, note)

    def _real_extract(self, url):
        category, playlist_id = re.match(self._VALID_URL, url).groups()
        if category == 'show':
            category = 'tvshow'
        if category == 'tv':
            category = 'tvplay'

        playlist_detail = self._call_api(
            'xqinfo', category, playlist_id, 'Download playlist JSON metadata')

        playlist_title = playlist_detail['title']
        playlist_description = unescapeHTML(playlist_detail.get('intro'))

        episodes_detail = self._call_api(
            'xqsingle', category, playlist_id, 'Download episodes JSON metadata')

        entries = [self.url_result(
            episode['url'], video_title=episode['title']
        ) for episode in episodes_detail['videos']]

        return self.playlist_result(
            entries, playlist_id, playlist_title, playlist_description)
