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
    int_or_none,
    mimetype2ext,
    parse_codecs,
    xpath_element,
    xpath_text,
)


class VideaIE(InfoExtractor):
    _VALID_URL = r'''(?x)
                    https?://
                        videa\.hu/
                        (?:
                            videok/(?:[^/]+/)*[^?#&]+-|
                            player\?.*?\bv=|
                            player/v/
                        )
                        (?P<id>[^?#&]+)
                    '''
    _TESTS = [{
        'url': 'http://videa.hu/videok/allatok/az-orult-kigyasz-285-kigyot-kigyo-8YfIAjxwWGwT8HVQ',
        'md5': '97a7af41faeaffd9f1fc864a7c7e7603',
        'info_dict': {
            'id': '8YfIAjxwWGwT8HVQ',
            'ext': 'mp4',
            'title': 'Az őrült kígyász 285 kígyót enged szabadon',
            'thumbnail': 'http://videa.hu/static/still/1.4.1.1007274.1204470.3',
            'duration': 21,
        },
    }, {
        'url': 'http://videa.hu/videok/origo/jarmuvek/supercars-elozes-jAHDWfWSJH5XuFhH',
        'only_matching': True,
    }, {
        'url': 'http://videa.hu/player?v=8YfIAjxwWGwT8HVQ',
        'only_matching': True,
    }, {
        'url': 'http://videa.hu/player/v/8YfIAjxwWGwT8HVQ?autoplay=1',
        'only_matching': True,
    }]

    @staticmethod
    def _extract_urls(webpage):
        return [url for _, url in re.findall(
            r'<iframe[^>]+src=(["\'])(?P<url>(?:https?:)?//videa\.hu/player\?.*?\bv=.+?)\1',
            webpage)]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        info = self._download_xml(
            'http://videa.hu/videaplayer_get_xml.php', video_id,
            query={'v': video_id})

        video = xpath_element(info, './/video', 'video', fatal=True)
        sources = xpath_element(info, './/video_sources', 'sources', fatal=True)

        title = xpath_text(video, './title', fatal=True)

        formats = []
        for source in sources.findall('./video_source'):
            source_url = source.text
            if not source_url:
                continue
            f = parse_codecs(source.get('codecs'))
            f.update({
                'url': source_url,
                'ext': mimetype2ext(source.get('mimetype')) or 'mp4',
                'format_id': source.get('name'),
                'width': int_or_none(source.get('width')),
                'height': int_or_none(source.get('height')),
            })
            formats.append(f)
        self._sort_formats(formats)

        thumbnail = xpath_text(video, './poster_src')
        duration = int_or_none(xpath_text(video, './duration'))

        age_limit = None
        is_adult = xpath_text(video, './is_adult_content', default=None)
        if is_adult:
            age_limit = 18 if is_adult == '1' else 0

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'age_limit': age_limit,
            'formats': formats,
        }
