import unittest

import unicodecsv as csv
import mzgtfs.feed
import mzgtfs.entities
import make_all_accessible
import util

class TestAccessible(unittest.TestCase):
    """ testing 1234 """

    def setUp(self):
        self.f = mzgtfs.feed.Feed(filename='artxanda-gtfs.zip')
        self.f.preload()

    def test_stops(self):
        
        make_all_accessible.make_accessible_stops(self.f)
        print self.f.stops()[0].json()
        assert self.f.stops()[0].get('wheelchair_boarding') == 1

    def test_trips(self):
        make_all_accessible.make_accessible_trips(self.f)
        assert self.f.trips()[0].get('wheelchair_accessible') == 1 
    
