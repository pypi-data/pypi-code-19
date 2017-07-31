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
from .brightcove import BrightcoveNewIE
from ..utils import (
    int_or_none,
    parse_age_limit,
    smuggle_url,
    unescapeHTML,
)


class VrakIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?vrak\.tv/videos\?.*?\btarget=(?P<id>[\d.]+)'
    _TEST = {
        'url': 'http://www.vrak.tv/videos?target=1.2306782&filtre=emission&id=1.1806721',
        'info_dict': {
            'id': '5345661243001',
            'ext': 'mp4',
            'title': 'Obésité, film de hockey et Roseline Filion',
            'timestamp': 1488492126,
            'upload_date': '20170302',
            'uploader_id': '2890187628001',
            'creator': 'VRAK.TV',
            'age_limit': 8,
            'series': 'ALT (Actualité Légèrement Tordue)',
            'episode': 'Obésité, film de hockey et Roseline Filion',
            'tags': list,
        },
        'params': {
            'skip_download': True,
        },
    }
    BRIGHTCOVE_URL_TEMPLATE = 'http://players.brightcove.net/2890187628001/default_default/index.html?videoId=%s'

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        title = self._html_search_regex(
            r'<h\d\b[^>]+\bclass=["\']videoTitle["\'][^>]*>([^<]+)',
            webpage, 'title', default=None) or self._og_search_title(webpage)

        content = self._parse_json(
            self._search_regex(
                r'data-player-options-content=(["\'])(?P<content>{.+?})\1',
                webpage, 'content', default='{}', group='content'),
            video_id, transform_source=unescapeHTML)

        ref_id = content.get('refId') or self._search_regex(
            r'refId&quot;:&quot;([^&]+)&quot;', webpage, 'ref id')

        brightcove_id = self._search_regex(
            r'''(?x)
                java\.lang\.String\s+value\s*=\s*["']brightcove\.article\.\d+\.%s
                [^>]*
                java\.lang\.String\s+value\s*=\s*["'](\d+)
            ''' % re.escape(ref_id), webpage, 'brightcove id')

        return {
            '_type': 'url_transparent',
            'ie_key': BrightcoveNewIE.ie_key(),
            'url': smuggle_url(
                self.BRIGHTCOVE_URL_TEMPLATE % brightcove_id,
                {'geo_countries': ['CA']}),
            'id': brightcove_id,
            'description': content.get('description'),
            'creator': content.get('brand'),
            'age_limit': parse_age_limit(content.get('rating')),
            'series': content.get('showName') or content.get(
                'episodeName'),  # this is intentional
            'season_number': int_or_none(content.get('seasonNumber')),
            'episode': title,
            'episode_number': int_or_none(content.get('episodeNumber')),
            'tags': content.get('tags', []),
        }
