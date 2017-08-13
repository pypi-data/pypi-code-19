
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

import sys

from .common import InfoExtractor
from ..utils import ExtractorError


class CommonMistakesIE(InfoExtractor):
    IE_DESC = False  # Do not list
    _VALID_URL = r'''(?x)
        (?:url|URL)$
    '''

    _TESTS = [{
        'url': 'url',
        'only_matching': True,
    }, {
        'url': 'URL',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        msg = (
            'You\'ve asked avideo to download the URL "%s". '
            'That doesn\'t make any sense. '
            'Simply remove the parameter in your command or configuration.'
        ) % url
        if not self._downloader.params.get('verbose'):
            msg += ' Add -v to the command line to see what arguments and configuration avideo got.'
        raise ExtractorError(msg, expected=True)


class UnicodeBOMIE(InfoExtractor):
        IE_DESC = False
        _VALID_URL = r'(?P<bom>\ufeff)(?P<id>.*)$'

        # Disable test for python 3.2 since BOM is broken in re in this version
        # (see https://github.com/rg3/youtube-dl/issues/9751)
        _TESTS = [] if (3, 0) < sys.version_info <= (3, 3) else [{
            'url': '\ufeffhttp://www.youtube.com/watch?v=BaW_jenozKc',
            'only_matching': True,
        }]

        def _real_extract(self, url):
            real_url = self._match_id(url)
            self.report_warning(
                'Your URL starts with a Byte Order Mark (BOM). '
                'Removing the BOM and looking for "%s" ...' % real_url)
            return self.url_result(real_url)
