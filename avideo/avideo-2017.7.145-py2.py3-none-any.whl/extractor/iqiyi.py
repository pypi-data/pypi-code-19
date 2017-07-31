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

import hashlib
import itertools
import re
import time

from .common import InfoExtractor
from ..compat import (
    compat_str,
    compat_urllib_parse_urlencode,
)
from ..utils import (
    clean_html,
    decode_packed_codes,
    get_element_by_id,
    get_element_by_attribute,
    ExtractorError,
    ohdave_rsa_encrypt,
    remove_start,
)


def md5_text(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()





class IqiyiIE(InfoExtractor):
    IE_NAME = 'iqiyi'
    IE_DESC = '爱奇艺'

    _VALID_URL = r'https?://(?:(?:[^.]+\.)?iqiyi\.com|www\.pps\.tv)/.+\.html'

    _NETRC_MACHINE = 'iqiyi'

    _TESTS = [{
        'url': 'http://www.iqiyi.com/v_19rrojlavg.html',
        # MD5 checksum differs on my machine and Travis CI
        'info_dict': {
            'id': '9c1fb1b99d192b21c559e5a1a2cb3c73',
            'ext': 'mp4',
            'title': '美国德州空中惊现奇异云团 酷似UFO',
        }
    }, {
        'url': 'http://www.iqiyi.com/v_19rrhnnclk.html',
        'md5': 'b7dc800a4004b1b57749d9abae0472da',
        'info_dict': {
            'id': 'e3f585b550a280af23c98b6cb2be19fb',
            'ext': 'mp4',
            # This can be either Simplified Chinese or Traditional Chinese
            'title': r're:^(?:名侦探柯南 国语版：第752集 迫近灰原秘密的黑影 下篇|名偵探柯南 國語版：第752集 迫近灰原秘密的黑影 下篇)$',
        },
        'skip': 'Geo-restricted to China',
    }, {
        'url': 'http://www.iqiyi.com/w_19rt6o8t9p.html',
        'only_matching': True,
    }, {
        'url': 'http://www.iqiyi.com/a_19rrhbc6kt.html',
        'only_matching': True,
    }, {
        'url': 'http://yule.iqiyi.com/pcb.html',
        'info_dict': {
            'id': '4a0af228fddb55ec96398a364248ed7f',
            'ext': 'mp4',
            'title': '第2017-04-21期 女艺人频遭极端粉丝骚扰',
        },
    }, {
        # VIP-only video. The first 2 parts (6 minutes) are available without login
        # MD5 sums omitted as values are different on Travis CI and my machine
        'url': 'http://www.iqiyi.com/v_19rrny4w8w.html',
        'info_dict': {
            'id': 'f3cf468b39dddb30d676f89a91200dc1',
            'ext': 'mp4',
            'title': '泰坦尼克号',
        },
        'skip': 'Geo-restricted to China',
    }, {
        'url': 'http://www.iqiyi.com/a_19rrhb8ce1.html',
        'info_dict': {
            'id': '202918101',
            'title': '灌篮高手 国语版',
        },
        'playlist_count': 101,
    }, {
        'url': 'http://www.pps.tv/w_19rrbav0ph.html',
        'only_matching': True,
    }]

    _FORMATS_MAP = {
        '96': 1,    # 216p, 240p
        '1': 2,     # 336p, 360p
        '2': 3,     # 480p, 504p
        '21': 4,    # 504p
        '4': 5,     # 720p
        '17': 5,    # 720p
        '5': 6,     # 1072p, 1080p
        '18': 7,    # 1080p
    }

    def _real_initialize(self):
        self._login()

    @staticmethod
    def _rsa_fun(data):
        # public key extracted from http://static.iqiyi.com/js/qiyiV2/20160129180840/jobs/i18n/i18nIndex.js
        N = 0xab86b6371b5318aaa1d3c9e612a9f1264f372323c8c0f19875b5fc3b3fd3afcc1e5bec527aa94bfa85bffc157e4245aebda05389a5357b75115ac94f074aefcd
        e = 65537

        return ohdave_rsa_encrypt(data, e, N)

    def _login(self):
        raise ExtractorError("iQiyi's non-free authentication algorithm has made login impossible", expected=True)

    def get_raw_data(self, tvid, video_id):
        tm = int(time.time() * 1000)

        key = 'd5fb4bd9d50c4be6948c97edd7254b0e'
        sc = md5_text(compat_str(tm) + key + tvid)
        params = {
            'tvid': tvid,
            'vid': video_id,
            'src': '76f90cbd92f94a2e925d83e8ccd22cb7',
            'sc': sc,
            't': tm,
        }

        return self._download_json(
            'http://cache.m.iqiyi.com/jp/tmts/%s/%s/' % (tvid, video_id),
            video_id, transform_source=lambda s: remove_start(s, 'var tvInfoJs='),
            query=params, headers=self.geo_verification_headers())

    def _extract_playlist(self, webpage):
        PAGE_SIZE = 50

        links = re.findall(
            r'<a[^>]+class="site-piclist_pic_link"[^>]+href="(http://www\.iqiyi\.com/.+\.html)"',
            webpage)
        if not links:
            return

        album_id = self._search_regex(
            r'albumId\s*:\s*(\d+),', webpage, 'album ID')
        album_title = self._search_regex(
            r'data-share-title="([^"]+)"', webpage, 'album title', fatal=False)

        entries = list(map(self.url_result, links))

        # Start from 2 because links in the first page are already on webpage
        for page_num in itertools.count(2):
            pagelist_page = self._download_webpage(
                'http://cache.video.qiyi.com/jp/avlist/%s/%d/%d/' % (album_id, page_num, PAGE_SIZE),
                album_id,
                note='Download playlist page %d' % page_num,
                errnote='Failed to download playlist page %d' % page_num)
            pagelist = self._parse_json(
                remove_start(pagelist_page, 'var tvInfoJs='), album_id)
            vlist = pagelist['data']['vlist']
            for item in vlist:
                entries.append(self.url_result(item['vurl']))
            if len(vlist) < PAGE_SIZE:
                break

        return self.playlist_result(entries, album_id, album_title)

    def _real_extract(self, url):
        webpage = self._download_webpage(
            url, 'temp_id', note='download video page')

        # There's no simple way to determine whether an URL is a playlist or not
        # Sometimes there are playlist links in individual videos, so treat it
        # as a single video first
        tvid = self._search_regex(
            r'data-(?:player|shareplattrigger)-tvid\s*=\s*[\'"](\d+)', webpage, 'tvid', default=None)
        if tvid is None:
            playlist_result = self._extract_playlist(webpage)
            if playlist_result:
                return playlist_result
            raise ExtractorError('Can\'t find any video')

        video_id = self._search_regex(
            r'data-(?:player|shareplattrigger)-videoid\s*=\s*[\'"]([a-f\d]+)', webpage, 'video_id')

        formats = []
        for _ in range(5):
            raw_data = self.get_raw_data(tvid, video_id)

            if raw_data['code'] != 'A00000':
                if raw_data['code'] == 'A00111':
                    self.raise_geo_restricted()
                raise ExtractorError('Unable to load data. Error code: ' + raw_data['code'])

            data = raw_data['data']

            for stream in data['vidl']:
                if 'm3utx' not in stream:
                    continue
                vd = compat_str(stream['vd'])
                formats.append({
                    'url': stream['m3utx'],
                    'format_id': vd,
                    'ext': 'mp4',
                    'preference': self._FORMATS_MAP.get(vd, -1),
                    'protocol': 'm3u8_native',
                })

            if formats:
                break

            self._sleep(5, video_id)

        self._sort_formats(formats)
        title = (get_element_by_id('widget-videotitle', webpage) or
                 clean_html(get_element_by_attribute('class', 'mod-play-tit', webpage)) or
                 self._html_search_regex(r'<span[^>]+data-videochanged-title="word"[^>]*>([^<]+)</span>', webpage, 'title'))

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
        }
