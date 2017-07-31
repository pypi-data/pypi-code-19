
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

from ..utils import (
    int_or_none,
    str_to_int,
    unified_strdate,
)
from .keezmovies import KeezMoviesIE


class MofosexIE(KeezMoviesIE):
    _VALID_URL = r'https?://(?:www\.)?mofosex\.com/videos/(?P<id>\d+)/(?P<display_id>[^/?#&.]+)\.html'
    _TESTS = [{
        'url': 'http://www.mofosex.com/videos/318131/amateur-teen-playing-and-masturbating-318131.html',
        'md5': '39a15853632b7b2e5679f92f69b78e91',
        'info_dict': {
            'id': '318131',
            'display_id': 'amateur-teen-playing-and-masturbating-318131',
            'ext': 'mp4',
            'title': 'amateur teen playing and masturbating',
            'thumbnail': r're:^https?://.*\.jpg$',
            'upload_date': '20121114',
            'view_count': int,
            'like_count': int,
            'dislike_count': int,
            'age_limit': 18,
        }
    }, {
        # This video is no longer available
        'url': 'http://www.mofosex.com/videos/5018/japanese-teen-music-video.html',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        webpage, info = self._extract_info(url)

        view_count = str_to_int(self._search_regex(
            r'VIEWS:</span>\s*([\d,.]+)', webpage, 'view count', fatal=False))
        like_count = int_or_none(self._search_regex(
            r'id=["\']amountLikes["\'][^>]*>(\d+)', webpage,
            'like count', fatal=False))
        dislike_count = int_or_none(self._search_regex(
            r'id=["\']amountDislikes["\'][^>]*>(\d+)', webpage,
            'like count', fatal=False))
        upload_date = unified_strdate(self._html_search_regex(
            r'Added:</span>([^<]+)', webpage, 'upload date', fatal=False))

        info.update({
            'view_count': view_count,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'upload_date': upload_date,
            'thumbnail': self._og_search_thumbnail(webpage),
        })

        return info
