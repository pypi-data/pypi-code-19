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
from ..utils import (
    parse_duration,
    unified_strdate,
)


class SapoIE(InfoExtractor):
    IE_DESC = 'SAPO Vídeos'
    _VALID_URL = r'https?://(?:(?:v2|www)\.)?videos\.sapo\.(?:pt|cv|ao|mz|tl)/(?P<id>[\da-zA-Z]{20})'

    _TESTS = [
        {
            'url': 'http://videos.sapo.pt/UBz95kOtiWYUMTA5Ghfi',
            'md5': '79ee523f6ecb9233ac25075dee0eda83',
            'note': 'SD video',
            'info_dict': {
                'id': 'UBz95kOtiWYUMTA5Ghfi',
                'ext': 'mp4',
                'title': 'Benfica - Marcas na Hitória',
                'description': 'md5:c9082000a128c3fd57bf0299e1367f22',
                'duration': 264,
                'uploader': 'tiago_1988',
                'upload_date': '20080229',
                'categories': ['benfica', 'cabral', 'desporto', 'futebol', 'geovanni', 'hooijdonk', 'joao', 'karel', 'lisboa', 'miccoli'],
            },
        },
        {
            'url': 'http://videos.sapo.pt/IyusNAZ791ZdoCY5H5IF',
            'md5': '90a2f283cfb49193fe06e861613a72aa',
            'note': 'HD video',
            'info_dict': {
                'id': 'IyusNAZ791ZdoCY5H5IF',
                'ext': 'mp4',
                'title': 'Codebits VII - Report',
                'description': 'md5:6448d6fd81ce86feac05321f354dbdc8',
                'duration': 144,
                'uploader': 'codebits',
                'upload_date': '20140427',
                'categories': ['codebits', 'codebits2014'],
            },
        },
        {
            'url': 'http://v2.videos.sapo.pt/yLqjzPtbTimsn2wWBKHz',
            'md5': 'e5aa7cc0bdc6db9b33df1a48e49a15ac',
            'note': 'v2 video',
            'info_dict': {
                'id': 'yLqjzPtbTimsn2wWBKHz',
                'ext': 'mp4',
                'title': 'Hipnose Condicionativa 4',
                'description': 'md5:ef0481abf8fb4ae6f525088a6dadbc40',
                'duration': 692,
                'uploader': 'sapozen',
                'upload_date': '20090609',
                'categories': ['condicionativa', 'heloisa', 'hipnose', 'miranda', 'sapo', 'zen'],
            },
        },
    ]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')

        item = self._download_xml(
            'http://rd3.videos.sapo.pt/%s/rss2' % video_id, video_id).find('./channel/item')

        title = item.find('./title').text
        description = item.find('./{http://videos.sapo.pt/mrss/}synopse').text
        thumbnail = item.find('./{http://search.yahoo.com/mrss/}content').get('url')
        duration = parse_duration(item.find('./{http://videos.sapo.pt/mrss/}time').text)
        uploader = item.find('./{http://videos.sapo.pt/mrss/}author').text
        upload_date = unified_strdate(item.find('./pubDate').text)
        view_count = int(item.find('./{http://videos.sapo.pt/mrss/}views').text)
        comment_count = int(item.find('./{http://videos.sapo.pt/mrss/}comment_count').text)
        tags = item.find('./{http://videos.sapo.pt/mrss/}tags').text
        categories = tags.split() if tags else []
        age_limit = 18 if item.find('./{http://videos.sapo.pt/mrss/}m18').text == 'true' else 0

        video_url = item.find('./{http://videos.sapo.pt/mrss/}videoFile').text
        video_size = item.find('./{http://videos.sapo.pt/mrss/}videoSize').text.split('x')

        formats = [{
            'url': video_url,
            'ext': 'mp4',
            'format_id': 'sd',
            'width': int(video_size[0]),
            'height': int(video_size[1]),
        }]

        if item.find('./{http://videos.sapo.pt/mrss/}HD').text == 'true':
            formats.append({
                'url': re.sub(r'/mov/1$', '/mov/39', video_url),
                'ext': 'mp4',
                'format_id': 'hd',
                'width': 1280,
                'height': 720,
            })

        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
            'duration': duration,
            'uploader': uploader,
            'upload_date': upload_date,
            'view_count': view_count,
            'comment_count': comment_count,
            'categories': categories,
            'age_limit': age_limit,
            'formats': formats,
        }
