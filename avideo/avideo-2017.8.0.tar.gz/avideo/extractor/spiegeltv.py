
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
from .nexx import NexxIE


class SpiegeltvIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?spiegel\.tv/videos/(?P<id>\d+)'
    _TEST = {
        'url': 'http://www.spiegel.tv/videos/161681-flug-mh370/',
        'only_matching': True,
    }

    def _real_extract(self, url):
        return self.url_result(
            'https://api.nexx.cloud/v3/748/videos/byid/%s'
            % self._match_id(url), ie=NexxIE.ie_key())
