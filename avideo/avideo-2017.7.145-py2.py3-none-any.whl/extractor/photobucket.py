
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

import json
import re

from .common import InfoExtractor
from ..compat import compat_urllib_parse_unquote


class PhotobucketIE(InfoExtractor):
    _VALID_URL = r'https?://(?:[a-z0-9]+\.)?photobucket\.com/.*(([\?\&]current=)|_)(?P<id>.*)\.(?P<ext>(flv)|(mp4))'
    _TEST = {
        'url': 'http://media.photobucket.com/user/rachaneronas/media/TiredofLinkBuildingTryBacklinkMyDomaincom_zpsc0c3b9fa.mp4.html?filters[term]=search&filters[primary]=videos&filters[secondary]=images&sort=1&o=0',
        'md5': '7dabfb92b0a31f6c16cebc0f8e60ff99',
        'info_dict': {
            'id': 'zpsc0c3b9fa',
            'ext': 'mp4',
            'timestamp': 1367669341,
            'upload_date': '20130504',
            'uploader': 'rachaneronas',
            'title': 'Tired of Link Building? Try BacklinkMyDomain.com!',
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        video_extension = mobj.group('ext')

        webpage = self._download_webpage(url, video_id)

        # Extract URL, uploader, and title from webpage
        self.report_extraction(video_id)
        info_json = self._search_regex(r'Pb\.Data\.Shared\.put\(Pb\.Data\.Shared\.MEDIA, (.*?)\);',
                                       webpage, 'info json')
        info = json.loads(info_json)
        url = compat_urllib_parse_unquote(self._html_search_regex(r'file=(.+\.mp4)', info['linkcodes']['html'], 'url'))
        return {
            'id': video_id,
            'url': url,
            'uploader': info['username'],
            'timestamp': info['creationDate'],
            'title': info['title'],
            'ext': video_extension,
            'thumbnail': info['thumbUrl'],
        }
