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


class InaIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?ina\.fr/video/(?P<id>I?[A-Z0-9]+)'
    _TEST = {
        'url': 'http://www.ina.fr/video/I12055569/francois-hollande-je-crois-que-c-est-clair-video.html',
        'md5': 'a667021bf2b41f8dc6049479d9bb38a3',
        'info_dict': {
            'id': 'I12055569',
            'ext': 'mp4',
            'title': 'François Hollande "Je crois que c\'est clair"',
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)

        video_id = mobj.group('id')
        mrss_url = 'http://player.ina.fr/notices/%s.mrss' % video_id
        info_doc = self._download_xml(mrss_url, video_id)

        self.report_extraction(video_id)

        video_url = info_doc.find('.//{http://search.yahoo.com/mrss/}player').attrib['url']

        return {
            'id': video_id,
            'url': video_url,
            'title': info_doc.find('.//title').text,
        }
