#!/usr/bin/env python

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

# Allow direct execution
import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test.helper import FakeYDL


from avideo.extractor import (
    YoutubePlaylistIE,
    YoutubeIE,
)


class TestYoutubeLists(unittest.TestCase):
    def assertIsPlaylist(self, info):
        """Make sure the info has '_type' set to 'playlist'"""
        self.assertEqual(info['_type'], 'playlist')

    def test_youtube_playlist_noplaylist(self):
        dl = FakeYDL()
        dl.params['noplaylist'] = True
        ie = YoutubePlaylistIE(dl)
        result = ie.extract('https://www.youtube.com/watch?v=FXxLjLQi3Fg&list=PLwiyx1dc3P2JR9N8gQaQN_BCvlSlap7re')
        self.assertEqual(result['_type'], 'url')
        self.assertEqual(YoutubeIE().extract_id(result['url']), 'FXxLjLQi3Fg')

    def test_youtube_course(self):
        dl = FakeYDL()
        ie = YoutubePlaylistIE(dl)
        # TODO find a > 100 (paginating?) videos course
        result = ie.extract('https://www.youtube.com/course?list=ECUl4u3cNGP61MdtwGTqZA0MreSaDybji8')
        entries = list(result['entries'])
        self.assertEqual(YoutubeIE().extract_id(entries[0]['url']), 'j9WZyLZCBzs')
        self.assertEqual(len(entries), 25)
        self.assertEqual(YoutubeIE().extract_id(entries[-1]['url']), 'rYefUsYuEp0')

    def test_youtube_mix(self):
        dl = FakeYDL()
        ie = YoutubePlaylistIE(dl)
        result = ie.extract('https://www.youtube.com/watch?v=W01L70IGBgE&index=2&list=RDOQpdSVF_k_w')
        entries = result['entries']
        self.assertTrue(len(entries) >= 50)
        original_video = entries[0]
        self.assertEqual(original_video['id'], 'OQpdSVF_k_w')

    def test_youtube_toptracks(self):
        print('Skipping: The playlist page gives error 500')
        return
        dl = FakeYDL()
        ie = YoutubePlaylistIE(dl)
        result = ie.extract('https://www.youtube.com/playlist?list=MCUS')
        entries = result['entries']
        self.assertEqual(len(entries), 100)

    def test_youtube_flat_playlist_titles(self):
        dl = FakeYDL()
        dl.params['extract_flat'] = True
        ie = YoutubePlaylistIE(dl)
        result = ie.extract('https://www.youtube.com/playlist?list=PLwiyx1dc3P2JR9N8gQaQN_BCvlSlap7re')
        self.assertIsPlaylist(result)
        for entry in result['entries']:
            self.assertTrue(entry.get('title'))


if __name__ == '__main__':
    unittest.main()
