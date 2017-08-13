
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

from .common import PostProcessor


class MetadataFromTitlePP(PostProcessor):
    def __init__(self, downloader, titleformat):
        super(MetadataFromTitlePP, self).__init__(downloader)
        self._titleformat = titleformat
        self._titleregex = (self.format_to_regex(titleformat)
                            if re.search(r'%\(\w+\)s', titleformat)
                            else titleformat)

    def format_to_regex(self, fmt):
        r"""
        Converts a string like
           '%(title)s - %(artist)s'
        to a regex like
           '(?P<title>.+)\ \-\ (?P<artist>.+)'
        """
        lastpos = 0
        regex = ''
        # replace %(..)s with regex group and escape other string parts
        for match in re.finditer(r'%\((\w+)\)s', fmt):
            regex += re.escape(fmt[lastpos:match.start()])
            regex += r'(?P<' + match.group(1) + '>.+)'
            lastpos = match.end()
        if lastpos < len(fmt):
            regex += re.escape(fmt[lastpos:])
        return regex

    def run(self, info):
        title = info['title']
        match = re.match(self._titleregex, title)
        if match is None:
            self._downloader.to_screen(
                '[fromtitle] Could not interpret title of video as "%s"'
                % self._titleformat)
            return [], info
        for attribute, value in match.groupdict().items():
            info[attribute] = value
            self._downloader.to_screen(
                '[fromtitle] parsed %s: %s'
                % (attribute, value if value is not None else 'NA'))

        return [], info
