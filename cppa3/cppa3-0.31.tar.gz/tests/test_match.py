
import unittest, cppa3, logging, lxml, os
from cppa3.match import match

from inspect import getsourcefile
from os.path import abspath, dirname, join

from copy import deepcopy

class MatchTestCase( unittest.TestCase ):

    def setUp(self):
        logging.getLogger('').handlers = []
        logging.basicConfig(level=logging.DEBUG,
                            filename="match_test.log")
        thisdir = dirname(abspath(getsourcefile(lambda:0)))
        self.unify_testdatadir = join(thisdir,'data')
        self.parser = lxml.etree.XMLParser(remove_blank_text=True)

    def do_reverse_match(self, id):
        logging.info('------------------')
        logging.info('Running test {}'.format(id))
        for letter in ['a','b']:
            logging.info('Match CPP {} against CPA for id {}'.format(letter, id))
            # Reuse the data from the unify test set.  Each CPP that
            # was successfully unified into a CPA should match that CPA
            cpp_file = os.path.join(self.unify_testdatadir,'cpp_{}_{}.xml'.format(letter, id))
            cpp =  (lxml.etree.parse(cpp_file, self.parser)).getroot()
            cpa_file = os.path.join(self.unify_testdatadir,'cppa_ab_{}.xml'.format(id))
            cpa =  (lxml.etree.parse(cpa_file, self.parser)).getroot()
            partyname = match(cpp, cpa)
            logging.info('CPA {} matches CPP {} for party {}'.format(id, letter, partyname))

    def test_0001(self):
       self.do_reverse_match('0001')

    def test_0007(self):
       self.do_reverse_match('0007')

    def test_0008(self):
       self.do_reverse_match('0008')

    def test_0009(self):
       self.do_reverse_match('0009')

    def test_0060(self):
       self.do_reverse_match('0060')

    def test_0300(self):
       self.do_reverse_match('0300')

    def test_1000(self):
       self.do_reverse_match('1000')

    def test_1001(self):
       self.do_reverse_match('1001')

    def test_1002(self):
       self.do_reverse_match('1002')

    def test_1006(self):
       self.do_reverse_match('1006')

    def test_1007(self):
       self.do_reverse_match('1007')

    def test_1010(self):
       self.do_reverse_match('1010')

    def test_1011(self):
       self.do_reverse_match('1011')


    # Skipped,  CPPs use channel features
    #
    #def test_1012(self):
    #   self.do_reverse_match('1012')
    #def test_1020(self):
    #   self.do_reverse_match('1020')

    def test_1100(self):
       self.do_reverse_match('1100')

    def test_1101(self):
       self.do_reverse_match('1101')

    def test_1102(self):
       self.do_reverse_match('1102')

    def test_1103(self):
       self.do_reverse_match('1103')

    def test_1120(self):
       self.do_reverse_match('1120')

    def test_1121(self):
       self.do_reverse_match('1121')

    def test_1124(self):
       self.do_reverse_match('1124')

    def test_1125(self):
       self.do_reverse_match('1125')

    def test_1126(self):
       self.do_reverse_match('1126')

    def test_1600(self):
       self.do_reverse_match('1600')


