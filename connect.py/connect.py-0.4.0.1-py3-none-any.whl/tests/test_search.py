# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2016-2017 GiovanniMCMXCIX

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import unittest
import connect


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.connect = connect.Client()

    def test_release(self):
        releases = self.connect.search_release('friends')
        print('\n[connect.Client.search_release] Found the following:')
        for release in releases:
            print('[{0.catalog_id}] Released on {0.release_date}, has {1} track(s) and with the title {0.title}'.format(release, len(release.tracks)))
        self.assertEqual(releases[0], self.connect.get_release('MCEP071'))

    def test_release_adv(self):
        releases = self.connect.search_release_advanced('FTW', 'Lets Be Friends')
        print('\n[connect.Client.search_release_advanced] Found the following:')
        for release in releases:
            print('[{0.catalog_id}] Released on {0.release_date}, has {1} track(s) and with the title {0.title}'.format(release, len(release.tracks)))
        self.assertEqual(releases[0], self.connect.get_release('MCS194'))

    def test_track(self):
        tracks = self.connect.search_track('you')
        print('\n[connect.Client.search_track] Found the following:')
        for track in tracks:
            print('{0.title} by {0.artists} with the genre(s) {1} and featured on {2} release(s)'.format(track, ', '.join(track.genres), len(track.albums)))
        self.assertEqual(tracks[0], self.connect.get_track('5175cd4e0695c7ac5d000033'))

    def test_track_adv(self):
        tracks = self.connect.search_track_advanced("Do You Don't You", 'Haywyre')
        print('\n[connect.Client.search_track_advanced] Found the following:')
        for track in tracks:
            print('{0.title} by {0.artists} with the genre(s) {1} and featured on {2} release(s)'.format(track, ', '.join(track.genres), len(track.albums)))
        self.assertEqual(tracks[0], self.connect.get_track('56a2773c5050dd875854cf85'))

    def test_artist(self):
        artists = self.connect.search_artist('grant')
        print('\n[connect.Client.search_artist] Found the following:')
        for artist in artists:
            print("{0.name}, that has {1} release(s) and it's featured on the following year(s): {2}".format(artist, len(artist.releases),
                                                                                                             ', '.join(str(year) for year in artist.years)))
        self.assertEqual(artists[1], self.connect.get_artist('grant'))

    def tearDown(self):
        self.connect.close()
