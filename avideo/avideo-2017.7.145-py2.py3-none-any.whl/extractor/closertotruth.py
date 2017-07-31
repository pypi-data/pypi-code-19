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


class CloserToTruthIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?closertotruth\.com/(?:[^/]+/)*(?P<id>[^/?#&]+)'
    _TESTS = [{
        'url': 'http://closertotruth.com/series/solutions-the-mind-body-problem#video-3688',
        'info_dict': {
            'id': '0_zof1ktre',
            'display_id': 'solutions-the-mind-body-problem',
            'ext': 'mov',
            'title': 'Solutions to the Mind-Body Problem?',
            'upload_date': '20140221',
            'timestamp': 1392956007,
            'uploader_id': 'CTTXML'
        },
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'http://closertotruth.com/episodes/how-do-brains-work',
        'info_dict': {
            'id': '0_iuxai6g6',
            'display_id': 'how-do-brains-work',
            'ext': 'mov',
            'title': 'How do Brains Work?',
            'upload_date': '20140221',
            'timestamp': 1392956024,
            'uploader_id': 'CTTXML'
        },
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'http://closertotruth.com/interviews/1725',
        'info_dict': {
            'id': '1725',
            'title': 'AyaFr-002',
        },
        'playlist_mincount': 2,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)

        webpage = self._download_webpage(url, display_id)

        partner_id = self._search_regex(
            r'<script[^>]+src=["\'].*?\b(?:partner_id|p)/(\d+)',
            webpage, 'kaltura partner_id')

        title = self._search_regex(
            r'<title>(.+?)\s*\|\s*.+?</title>', webpage, 'video title')

        select = self._search_regex(
            r'(?s)<select[^>]+id="select-version"[^>]*>(.+?)</select>',
            webpage, 'select version', default=None)
        if select:
            entry_ids = set()
            entries = []
            for mobj in re.finditer(
                    r'<option[^>]+value=(["\'])(?P<id>[0-9a-z_]+)(?:#.+?)?\1[^>]*>(?P<title>[^<]+)',
                    webpage):
                entry_id = mobj.group('id')
                if entry_id in entry_ids:
                    continue
                entry_ids.add(entry_id)
                entries.append({
                    '_type': 'url_transparent',
                    'url': 'kaltura:%s:%s' % (partner_id, entry_id),
                    'ie_key': 'Kaltura',
                    'title': mobj.group('title'),
                })
            if entries:
                return self.playlist_result(entries, display_id, title)

        entry_id = self._search_regex(
            r'<a[^>]+id=(["\'])embed-kaltura\1[^>]+data-kaltura=(["\'])(?P<id>[0-9a-z_]+)\2',
            webpage, 'kaltura entry_id', group='id')

        return {
            '_type': 'url_transparent',
            'display_id': display_id,
            'url': 'kaltura:%s:%s' % (partner_id, entry_id),
            'ie_key': 'Kaltura',
            'title': title
        }
