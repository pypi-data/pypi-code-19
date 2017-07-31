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
from .brightcove import BrightcoveLegacyIE
from ..compat import (
    compat_parse_qs,
    compat_urlparse,
)


class RMCDecouverteIE(InfoExtractor):
    _VALID_URL = r'https?://rmcdecouverte\.bfmtv\.com/mediaplayer-replay.*?\bid=(?P<id>\d+)'

    _TEST = {
        'url': 'http://rmcdecouverte.bfmtv.com/mediaplayer-replay/?id=13502&title=AQUAMEN:LES%20ROIS%20DES%20AQUARIUMS%20:UN%20DELICIEUX%20PROJET',
        'info_dict': {
            'id': '5419055995001',
            'ext': 'mp4',
            'title': 'UN DELICIEUX PROJET',
            'description': 'md5:63610df7c8b1fc1698acd4d0d90ba8b5',
            'uploader_id': '1969646226001',
            'upload_date': '20170502',
            'timestamp': 1493745308,
        },
        'params': {
            'skip_download': True,
        },
        'skip': 'only available for a week',
    }
    BRIGHTCOVE_URL_TEMPLATE = 'http://players.brightcove.net/1969646226001/default_default/index.html?videoId=%s'

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)
        brightcove_legacy_url = BrightcoveLegacyIE._extract_brightcove_url(webpage)
        if brightcove_legacy_url:
            brightcove_id = compat_parse_qs(compat_urlparse.urlparse(
                brightcove_legacy_url).query)['@videoPlayer'][0]
        else:
            brightcove_id = self._search_regex(
                r'data-video-id=["\'](\d+)', webpage, 'brightcove id')
        return self.url_result(
            self.BRIGHTCOVE_URL_TEMPLATE % brightcove_id, 'BrightcoveNew',
            brightcove_id)
