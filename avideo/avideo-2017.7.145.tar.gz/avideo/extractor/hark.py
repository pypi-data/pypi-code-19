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


class HarkIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?hark\.com/clips/(?P<id>.+?)-.+'
    _TEST = {
        'url': 'http://www.hark.com/clips/mmbzyhkgny-obama-beyond-the-afghan-theater-we-only-target-al-qaeda-on-may-23-2013',
        'md5': '6783a58491b47b92c7c1af5a77d4cbee',
        'info_dict': {
            'id': 'mmbzyhkgny',
            'ext': 'mp3',
            'title': 'Obama: \'Beyond The Afghan Theater, We Only Target Al Qaeda\' on May 23, 2013',
            'description': 'President Barack Obama addressed the nation live on May 23, 2013 in a speech aimed at addressing counter-terrorism policies including the use of drone strikes, detainees at Guantanamo Bay prison facility, and American citizens who are terrorists.',
            'duration': 11,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        data = self._download_json(
            'http://www.hark.com/clips/%s.json' % video_id, video_id)

        return {
            'id': video_id,
            'url': data['url'],
            'title': data['name'],
            'description': data.get('description'),
            'thumbnail': data.get('image_original'),
            'duration': data.get('duration'),
        }
