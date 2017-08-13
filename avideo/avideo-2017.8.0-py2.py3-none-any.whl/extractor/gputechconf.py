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


class GPUTechConfIE(InfoExtractor):
    _VALID_URL = r'https?://on-demand\.gputechconf\.com/gtc/2015/video/S(?P<id>\d+)\.html'
    _TEST = {
        'url': 'http://on-demand.gputechconf.com/gtc/2015/video/S5156.html',
        'md5': 'a8862a00a0fd65b8b43acc5b8e33f798',
        'info_dict': {
            'id': '5156',
            'ext': 'mp4',
            'title': 'Coordinating More Than 3 Million CUDA Threads for Social Network Analysis',
            'duration': 1219,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        root_path = self._search_regex(
            r'var\s+rootPath\s*=\s*"([^"]+)', webpage, 'root path',
            default='http://evt.dispeak.com/nvidia/events/gtc15/')
        xml_file_id = self._search_regex(
            r'var\s+xmlFileId\s*=\s*"([^"]+)', webpage, 'xml file id')

        return {
            '_type': 'url_transparent',
            'id': video_id,
            'url': '%sxml/%s.xml' % (root_path, xml_file_id),
            'ie_key': 'DigitallySpeaking',
        }
