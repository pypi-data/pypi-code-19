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
    float_or_none,
    xpath_text
)


class NuevoBaseIE(InfoExtractor):
    def _extract_nuevo(self, config_url, video_id, headers={}):
        config = self._download_xml(
            config_url, video_id, transform_source=lambda s: s.strip(),
            headers=headers)

        title = xpath_text(config, './title', 'title', fatal=True).strip()
        video_id = xpath_text(config, './mediaid', default=video_id)
        thumbnail = xpath_text(config, ['./image', './thumb'])
        duration = float_or_none(xpath_text(config, './duration'))

        formats = []
        for element_name, format_id in (('file', 'sd'), ('filehd', 'hd')):
            video_url = xpath_text(config, element_name)
            if video_url:
                formats.append({
                    'url': video_url,
                    'format_id': format_id,
                })
        self._check_formats(formats, video_id)

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'formats': formats
        }
