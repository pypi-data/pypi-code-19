'''
Created on Mar 17, 2017

@author: neil
'''
import unittest

from ncexplorer.frame.base import BaseFrame
from ncexplorer.app import parse_params

class TestProgressbar(object):

    def update(self, msg=""):
        pass
    def start(self, total_steps):
        pass
    def close(self):
        pass

class TestFrame(BaseFrame):
    
    def _display_matches(self, matches):
        self.matches = matches
    def _set_progressbar(self):
        pb = TestProgressbar()
        return pb


# Tests of all the acceptable search parameter syntaxes.
class TestSearchParamSyntax(unittest.TestCase):

    def test_no_space(self):
        self.assertEqual(
            {'key1': 'val1', 'key2': 'val2'},
            parse_params("key1=val1,key2=val2")
        )

    def test_extra_space(self):
        self.assertEqual(
            {'key1': 'val1', 'key2': 'val2'},
            parse_params("   key1    =    val1,    key2   =   val2   ")
        )

    def test_tab(self):
        self.assertEqual(
            {'key1': 'val1', 'key2': 'val2'},
            parse_params("key1    = val1,key2    = val2")
        )

    def test_single_quote(self):
        self.assertEqual(
            {'key1': 'val1', 'key2': 'val2'},
            parse_params("key1='val1', key2='val2'")
        )

    def test_space_in_val(self):
        self.assertEqual(
            {'key1': 'val 1', 'key2': 'val 2'},
            parse_params("key1 = 'val 1', key2 = 'val 2'")
        )
        
class TestSearchBase(unittest.TestCase):

    def test_baseframe_search_results(self):
        searchstr = ("experiment='lgm', time_frequency='monClim', "
                    + "institute='NCAR', variable='ta'")
        appframe = TestFrame('Test')
        matches = appframe.search(searchstr=searchstr)
        self.assertEqual(2, len(matches))


if __name__ == '__main__':
    unittest.main()