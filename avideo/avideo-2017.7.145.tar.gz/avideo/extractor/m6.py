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


class M6IE(InfoExtractor):
    IE_NAME = 'm6'
    _VALID_URL = r'https?://(?:www\.)?m6\.fr/[^/]+/videos/(?P<id>\d+)-[^\.]+\.html'

    _TEST = {
        'url': 'http://www.m6.fr/emission-les_reines_du_shopping/videos/11323908-emeline_est_la_reine_du_shopping_sur_le_theme_ma_fete_d_8217_anniversaire.html',
        'md5': '242994a87de2c316891428e0176bcb77',
        'info_dict': {
            'id': '11323908',
            'ext': 'mp4',
            'title': 'Emeline est la Reine du Shopping sur le thème « Ma fête d’anniversaire ! »',
            'description': 'md5:1212ae8fb4b7baa4dc3886c5676007c2',
            'duration': 100,
        }
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)
        return self.url_result('6play:%s' % video_id, 'SixPlay', video_id)
