import unittest
import collections
import json

import unicodecsv as csv
import mzgtfs.feed
import mzgtfs.entities
import add_fares
import util


class TestAddFares(unittest.TestCase):
    """ test adding fares"""

    def setUp(self):
        self.f = mzgtfs.feed.Feed(filename='artxanda-gtfs.zip')
        self.f.preload()
        self.attribute = {
            'fare_id' : '1',
            'price' : 0.95,
            'currency_type' : 'EUR',
            'payment_method' : 0,
            'transfers' : 0
        }

    def test_load(self):
        agency = self.f.agency('A1')
        assert agency.id() == 'A1'

    def test_add_attribute(self):
        add_fares.add_attribute(self.f, '1', self.attribute)

        assert len(self.f.fares()) == 1
        assert self.f.fare('1').get('price') == 0.95

    def test_add_rule_to_route(self):
        add_fares.add_rule_to_route(self.f, '1', 'R1', {})
        assert len(self.f.fare_rules()) == 1

    def test_add_regex_from_json(self):
        """ integration-level test"""

        with open('test_add_fares.json') as fares:
            input_json = json.load(fares)

        print repr(input_json)

        for fare_id, rules_attributes in input_json.iteritems():
            add_fares.add_fare_id(self.f, fare_id, rules_attributes)

        assert len(self.f.fare_rules()) == 1
        assert len(self.f.fares()) == 1
        assert self.f.fare('1').get('price') == '0.95'


    def test_write_out(self):
        add_fares.add_attribute(self.f, '1', self.attribute)
        add_fares.add_rule_to_route(self.f, '1', 'R1', {})

        files = ['fare_attributes.txt', 'fare_rules.txt']

        self.f.write('fare_attributes.txt', self.f.fares())
        self.f.write('fare_rules.txt', self.f.fare_rules())

        with open('fare_attributes.txt', 'rb') as o:
            reader = csv.DictReader(o)
            for row in reader:
                assert row['price'] == '0.95'
                assert row['currency_type'] == 'EUR'

        with open('fare_rules.txt', 'rb') as o:
            reader = csv.DictReader(o)
            for row in reader:
                assert row['fare_id'] == '1'
                assert row['route_id'] == 'R1'

        util.delete_temp_files(files)
