
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

from .nuevo import NuevoBaseIE


class NonkTubeIE(NuevoBaseIE):
    _VALID_URL = r'https?://(?:www\.)?nonktube\.com/(?:(?:video|embed)/|media/nuevo/embed\.php\?.*?\bid=)(?P<id>\d+)'
    _TESTS = [{
        'url': 'https://www.nonktube.com/video/118636/sensual-wife-uncensored-fucked-in-hairy-pussy-and-facialized',
        'info_dict': {
            'id': '118636',
            'ext': 'mp4',
            'title': 'Sensual Wife Uncensored Fucked In Hairy Pussy And Facialized',
            'age_limit': 18,
            'duration': 1150.98,
        },
        'params': {
            'skip_download': True,
        }
    }, {
        'url': 'https://www.nonktube.com/embed/118636',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        info = self._extract_nuevo(
            'https://www.nonktube.com/media/nuevo/econfig.php?key=%s'
            % video_id, video_id)

        info['age_limit'] = 18
        return info
