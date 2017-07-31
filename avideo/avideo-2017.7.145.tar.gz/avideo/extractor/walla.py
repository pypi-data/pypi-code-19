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
    xpath_text,
    int_or_none,
)


class WallaIE(InfoExtractor):
    _VALID_URL = r'https?://vod\.walla\.co\.il/[^/]+/(?P<id>\d+)/(?P<display_id>.+)'
    _TEST = {
        'url': 'http://vod.walla.co.il/movie/2642630/one-direction-all-for-one',
        'info_dict': {
            'id': '2642630',
            'display_id': 'one-direction-all-for-one',
            'ext': 'flv',
            'title': 'וואן דיירקשן: ההיסטריה',
            'description': 'md5:de9e2512a92442574cdb0913c49bc4d8',
            'thumbnail': r're:^https?://.*\.jpg',
            'duration': 3600,
        },
        'params': {
            # rtmp download
            'skip_download': True,
        }
    }

    _SUBTITLE_LANGS = {
        'עברית': 'heb',
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        display_id = mobj.group('display_id')

        video = self._download_xml(
            'http://video2.walla.co.il/?w=null/null/%s/@@/video/flv_pl' % video_id,
            display_id)

        item = video.find('./items/item')

        title = xpath_text(item, './title', 'title')
        description = xpath_text(item, './synopsis', 'description')
        thumbnail = xpath_text(item, './preview_pic', 'thumbnail')
        duration = int_or_none(xpath_text(item, './duration', 'duration'))

        subtitles = {}
        for subtitle in item.findall('./subtitles/subtitle'):
            lang = xpath_text(subtitle, './title')
            subtitles[self._SUBTITLE_LANGS.get(lang, lang)] = [{
                'ext': 'srt',
                'url': xpath_text(subtitle, './src'),
            }]

        formats = []
        for quality in item.findall('./qualities/quality'):
            format_id = xpath_text(quality, './title')
            fmt = {
                'url': 'rtmp://wafla.walla.co.il/vod',
                'play_path': xpath_text(quality, './src'),
                'player_url': 'http://isc.walla.co.il/w9/swf/video_swf/vod/WallaMediaPlayerAvod.swf',
                'page_url': url,
                'ext': 'flv',
                'format_id': xpath_text(quality, './title'),
            }
            m = re.search(r'^(?P<height>\d+)[Pp]', format_id)
            if m:
                fmt['height'] = int(m.group('height'))
            formats.append(fmt)
        self._sort_formats(formats)

        return {
            'id': video_id,
            'display_id': display_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'duration': duration,
            'formats': formats,
            'subtitles': subtitles,
        }
