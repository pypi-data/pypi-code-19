
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

from .nuevo import NuevoBaseIE


class LoveHomePornIE(NuevoBaseIE):
    _VALID_URL = r'https?://(?:www\.)?lovehomeporn\.com/video/(?P<id>\d+)(?:/(?P<display_id>[^/?#&]+))?'
    _TEST = {
        'url': 'http://lovehomeporn.com/video/48483/stunning-busty-brunette-girlfriend-sucking-and-riding-a-big-dick#menu',
        'info_dict': {
            'id': '48483',
            'display_id': 'stunning-busty-brunette-girlfriend-sucking-and-riding-a-big-dick',
            'ext': 'mp4',
            'title': 'Stunning busty brunette girlfriend sucking and riding a big dick',
            'age_limit': 18,
            'duration': 238.47,
        },
        'params': {
            'skip_download': True,
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        display_id = mobj.group('display_id')

        info = self._extract_nuevo(
            'http://lovehomeporn.com/media/nuevo/config.php?key=%s' % video_id,
            video_id)
        info.update({
            'display_id': display_id,
            'age_limit': 18
        })
        return info
