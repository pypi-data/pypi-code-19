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

from ..utils import (
    sanitized_Request,
    xpath_text,
    xpath_with_ns,
)


class RegioTVIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?regio-tv\.de/video/(?P<id>[0-9]+)'
    _TESTS = [{
        'url': 'http://www.regio-tv.de/video/395808.html',
        'info_dict': {
            'id': '395808',
            'ext': 'mp4',
            'title': 'Wir in Ludwigsburg',
            'description': 'Mit unseren zuckersüßen Adventskindern, außerdem besuchen wir die Abendsterne!',
        }
    }, {
        'url': 'http://www.regio-tv.de/video/395808',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        key = self._search_regex(
            r'key\s*:\s*(["\'])(?P<key>.+?)\1', webpage, 'key', group='key')
        title = self._og_search_title(webpage)

        SOAP_TEMPLATE = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><{0} xmlns="http://v.telvi.de/"><key xsi:type="xsd:string">{1}</key></{0}></soap:Body></soap:Envelope>'

        request = sanitized_Request(
            'http://v.telvi.de/',
            SOAP_TEMPLATE.format('GetHTML5VideoData', key).encode('utf-8'))
        video_data = self._download_xml(request, video_id, 'Downloading video XML')

        NS_MAP = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        }

        video_url = xpath_text(
            video_data, xpath_with_ns('.//video', NS_MAP), 'video url', fatal=True)
        thumbnail = xpath_text(
            video_data, xpath_with_ns('.//image', NS_MAP), 'thumbnail')
        description = self._og_search_description(
            webpage) or self._html_search_meta('description', webpage)

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'description': description,
            'thumbnail': thumbnail,
        }
