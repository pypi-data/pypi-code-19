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
from ..compat import compat_str


class VyboryMosIE(InfoExtractor):
    _VALID_URL = r'https?://vybory\.mos\.ru/(?:#precinct/|account/channels\?.*?\bstation_id=)(?P<id>\d+)'
    _TESTS = [{
        'url': 'http://vybory.mos.ru/#precinct/13636',
        'info_dict': {
            'id': '13636',
            'ext': 'mp4',
            'title': 're:^Участковая избирательная комиссия №2231 [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$',
            'description': 'Россия, Москва, улица Введенского, 32А',
            'is_live': True,
        },
        'params': {
            'skip_download': True,
        }
    }, {
        'url': 'http://vybory.mos.ru/account/channels?station_id=13636',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        station_id = self._match_id(url)

        channels = self._download_json(
            'http://vybory.mos.ru/account/channels?station_id=%s' % station_id,
            station_id, 'Downloading channels JSON')

        formats = []
        for cam_num, (sid, hosts, name, _) in enumerate(channels, 1):
            for num, host in enumerate(hosts, 1):
                formats.append({
                    'url': 'http://%s/master.m3u8?sid=%s' % (host, sid),
                    'ext': 'mp4',
                    'format_id': 'camera%d-host%d' % (cam_num, num),
                    'format_note': '%s, %s' % (name, host),
                })

        info = self._download_json(
            'http://vybory.mos.ru/json/voting_stations/%s/%s.json'
            % (compat_str(station_id)[:3], station_id),
            station_id, 'Downloading station JSON', fatal=False)

        return {
            'id': station_id,
            'title': self._live_title(info['name'] if info else station_id),
            'description': info.get('address'),
            'is_live': True,
            'formats': formats,
        }
