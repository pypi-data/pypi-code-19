# -*- coding: utf-8 -*-
# Copyright (C) Brian Moe, Branson Stephens (2015)
#
# This file is part of gracedb
#
# gracedb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gracedb.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import os
import json
import unittest
import argparse
from ligo.gracedb.rest import GraceDb, HTTPError
import voeventparse
import StringIO

TEST_SERVICE = "https://gracedb-test.ligo.org/api/"

# Utility for getting out a dictionary of ivorns and citation types
def get_citations_dict(v):
    citations_dict = {}
    for e in v.Citations.iterchildren():
        if e.tag == 'EventIVORN':
            ivorn = e.text
            citation_type = e.attrib['cite']
            citations_dict[ivorn] = citation_type
    return citations_dict

class TestGraceDbVOEvents(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global gracedb, graceid

        # Data directory
        testdatadir = os.path.join(os.path.dirname(__file__), "data")
        testdatadir = os.environ.get('TEST_DATA_DIR', testdatadir)

        # Set up client
        service = os.environ.get('TEST_SERVICE', TEST_SERVICE)
        gracedb = GraceDb(service)
        print("Using service {0}".format(service))

        # Create event and get its graceid
        eventFile = os.path.join(testdatadir, "cbc-lm.xml")
        r = gracedb.createEvent("Test", "gstlal", eventFile, "LowMass")
        event = r.json()
        graceid = event['graceid']

        # Upload fake skymap file to use later
        r = gracedb.writeLog(graceid, "Fake skymap file.",
            filename="fake_skymap.txt", filecontents="Fake skymap.",
            tagname="sky_loc")
        r = gracedb.writeLog(graceid, "Fake skymap image file.",
            filename="fake_skymap_image.txt",
            filecontents="Fake skymap image.", tagname="sky_loc")

    def test_create_preliminary_voevent(self):
        r = gracedb.createVOEvent(graceid, "Preliminary")
        rdict = r.json()
        self.assertTrue('voevent_type' in list(rdict.keys()))
        preliminary_voevent_text = rdict['text']

    def test_retrieve_preliminary_voevent(self):
        r = gracedb.voevents(graceid)
        voevent_list = r.json()['voevents']
        self.assertTrue(len(voevent_list) == 1 and 
            voevent_list[0]['voevent_type'] == 'PR')

    def test_create_update_voevent(self):
        r = gracedb.createVOEvent(graceid, "Update",
            skymap_filename="fake_skymap.txt", skymap_type="FAKE",
            skymap_image_filename="fake_skymap_image.txt")
        rdict = r.json()
        self.assertTrue('voevent_type' in list(rdict.keys()))

    def test_ivorns_unique(self):
        r = gracedb.voevents(graceid)
        voevent_list = r.json()['voevents']
        self.assertTrue(len(voevent_list) == 2)

        voevent_dict = {v['voevent_type']: v for v in voevent_list}
        preliminary_voevent = voeventparse.load(StringIO.StringIO(
            voevent_dict['PR']['text']))
        update_voevent = voeventparse.load(StringIO.StringIO(
            voevent_dict['UP']['text']))
        self.assertTrue(update_voevent.attrib['ivorn'] !=
                        preliminary_voevent.attrib['ivorn'])

    def test_citation_section(self):
        r = gracedb.voevents(graceid)
        voevent_list = r.json()['voevents']

        voevent_dict = {v['voevent_type']: v for v in voevent_list}
        preliminary_voevent = voeventparse.load(StringIO.StringIO(
            voevent_dict['PR']['text']))
        update_voevent = voeventparse.load(StringIO.StringIO(
            voevent_dict['UP']['text']))
        update_citations = get_citations_dict(update_voevent)
        preliminary_ivorn = preliminary_voevent.attrib['ivorn']
        self.assertEqual(update_citations[preliminary_ivorn], 'supersedes')

    def test_create_retraction_voevent(self):
        r = gracedb.createVOEvent(graceid, "Retraction")
        rdict = r.json()
        self.assertTrue('voevent_type' in list(rdict.keys()))
        #retraction_voevent = voeventparse.load(StringIO.StringIO(rdict['text']))

    def test_retraction_citations(self):
        r = gracedb.voevents(graceid)
        voevent_list = r.json()['voevents']

        voevent_dict = {v['voevent_type']: v for v in voevent_list}
        preliminary_voevent = voeventparse.load(StringIO.StringIO(
            voevent_dict['PR']['text']))
        update_voevent = voeventparse.load(StringIO.StringIO(
            voevent_dict['UP']['text']))
        retraction_voevent = voeventparse.load(StringIO.StringIO(
            voevent_dict['RE']['text']))
        # Parse retraction voevent and check for correct citations
        retraction_citations = get_citations_dict(retraction_voevent)
        preliminary_ivorn = preliminary_voevent.attrib['ivorn']
        update_ivorn = update_voevent.attrib['ivorn']
        self.assertTrue(retraction_citations[preliminary_ivorn] == 'retraction'
            and retraction_citations[update_ivorn] == 'retraction')

def test_suite():
    """
    A test suite is needed because there is some dependency between
    the successive individual tests; as a result, the order is important.
    """
    suite = unittest.TestSuite()
    suite.addTest(TestGraceDbVOEvents('test_create_preliminary_voevent'))
    suite.addTest(TestGraceDbVOEvents('test_retrieve_preliminary_voevent'))
    suite.addTest(TestGraceDbVOEvents('test_create_update_voevent'))
    suite.addTest(TestGraceDbVOEvents('test_ivorns_unique'))
    suite.addTest(TestGraceDbVOEvents('test_citation_section'))
    suite.addTest(TestGraceDbVOEvents('test_create_retraction_voevent'))
    suite.addTest(TestGraceDbVOEvents('test_retraction_citations'))
    return suite

if __name__ == '__main__':
    # Run tests
    unittest.TextTestRunner(verbosity=2, failfast=True).run(test_suite())

