
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


class DefenseGouvFrIE(InfoExtractor):
    IE_NAME = 'defense.gouv.fr'
    _VALID_URL = r'https?://.*?\.defense\.gouv\.fr/layout/set/ligthboxvideo/base-de-medias/webtv/(?P<id>[^/?#]*)'

    _TEST = {
        'url': 'http://www.defense.gouv.fr/layout/set/ligthboxvideo/base-de-medias/webtv/attaque-chimique-syrienne-du-21-aout-2013-1',
        'md5': '75bba6124da7e63d2d60b5244ec9430c',
        'info_dict': {
            'id': '11213',
            'ext': 'mp4',
            'title': 'attaque-chimique-syrienne-du-21-aout-2013-1'
        }
    }

    def _real_extract(self, url):
        title = self._match_id(url)
        webpage = self._download_webpage(url, title)

        video_id = self._search_regex(
            r"flashvars.pvg_id=\"(\d+)\";",
            webpage, 'ID')

        json_url = (
            'http://static.videos.gouv.fr/brightcovehub/export/json/%s' %
            video_id)
        info = self._download_json(json_url, title, 'Downloading JSON config')
        video_url = info['renditions'][0]['url']

        return {
            'id': video_id,
            'ext': 'mp4',
            'url': video_url,
            'title': title,
        }
