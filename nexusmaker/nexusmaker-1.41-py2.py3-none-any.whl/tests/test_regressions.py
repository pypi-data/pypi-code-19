import unittest
from nexusmaker import NexusMaker, Record

TESTDATA = [
    Record(Language="A", Word="eye", Item="", Cognacy="1"),
    Record(Language="B", Word="eye", Item="", Cognacy="1"),
    Record(Language="C", Word="eye", Item="", Cognacy="2"),
    Record(Language="D", Word="eye", Item="", Cognacy="2"),
    Record(Language="E", Word="eye", Item="", Cognacy=""),
]


class TestBugUniquesAndAmbig(unittest.TestCase):
    """
    Fix Bug caused by lru_cache on ._is_missing_for_word that made unique
    sites occur as single ones in blocks of missing states.
    """
    
    def setUp(self):
        self.maker = NexusMaker(data=TESTDATA)
        self.nex = self.maker.make()

    def test_cognate_sets(self):
        assert ('eye', '1') in self.maker.cognates
        assert ('eye', '2') in self.maker.cognates
        assert ('eye', 'u_1') in self.maker.cognates

        assert sorted(self.maker.cognates[('eye', '1')]) == ['A', 'B']
        assert sorted(self.maker.cognates[('eye', '2')]) == ['C', 'D']
        assert sorted(self.maker.cognates[('eye', 'u_1')]) == ['E']
    
    def test_is_missing_for_word(self):
        assert self.maker._is_missing_for_word('E', 'eye') == False
    
    def test_nexus(self):
        assert self.nex.data['eye_1'] == {
            'A': '1', 'B': '1',
            'C': '0', 'D': '0',
            'E': '0' # NOT '?'
        }
        assert self.nex.data['eye_2'] == {
            'A': '0', 'B': '0',
            'C': '1', 'D': '1',
            'E': '0' # NOT '?'
        }
        assert self.nex.data['eye_u_1'] == {
            'A': '0', 'B': '0',
            'C': '0', 'D': '0',
            'E': '1'
        }
        