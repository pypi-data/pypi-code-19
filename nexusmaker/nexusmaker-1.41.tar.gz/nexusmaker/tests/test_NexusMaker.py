import sys
import unittest

from nexusmaker import Record
from nexusmaker import NexusMaker, NexusMakerAscertained, NexusMakerAscertainedWords

TESTDATA = [
    Record(Language="A", Word="eye", Item="", Cognacy="1"),
    Record(Language="A", Word="leg", Item="", Cognacy="1"),
    Record(Language="A", Word="arm", Item="", Cognacy="1"),
    
    Record(Language="B", Word="eye", Item="", Cognacy="1"),
    Record(Language="B", Word="leg", Item="", Cognacy="2"),
    Record(Language="B", Word="arm", Item="", Cognacy="2"),
    
    Record(Language="C", Word="eye", Item="", Cognacy="1"),
    # No Record for C 'leg'
    Record(Language="C", Word="arm", Item="", Cognacy="3"),

    Record(Language="D", Word="eye", Item="", Cognacy="1", Loan=True),
    Record(Language="D", Word="leg", Item="", Cognacy="1"),
    Record(Language="D", Word="leg", Item="", Cognacy="2"),
    Record(Language="D", Word="arm", Item="", Cognacy="2,3"),
]


class TestNexusMakerInternals(unittest.TestCase):
    def test_error_on_non_record(self):
        with self.assertRaises(ValueError):
            NexusMaker(['1'])

    def test_error_on_bad_record(self):
        with self.assertRaises(ValueError):
            NexusMaker([
                Record(Word="leg", Item="", Cognacy="2")  # no language
            ])
        with self.assertRaises(ValueError):
            NexusMaker([
                Record(Language="French", Item="", Cognacy="2")  # no word
            ])
    
    def test_error_on_cognates_with_loans(self):
        """Test that we generate an error if a loan word enters .cognates()"""
        n = NexusMaker(TESTDATA)
        n.data.append(Record(Language="D", Word="eye", Item="", Cognacy="1", Loan=True))
        with self.assertRaises(ValueError):
            n.cognates
    
    def test_error_on_make_with_uniques_bigger_than_one(self):
        """
        Test that we generate an error in .make if a unique cognate set contains
        more than one language.
        """
        n = NexusMaker(TESTDATA)
        n.cognates
        n._cognates[('test', 'u_1')] = ["A", "B"]
        with self.assertRaises(AssertionError):
            n.make()


class TestNexusMaker(unittest.TestCase):
    model = NexusMaker

    def setUp(self):
        self.maker = self.model(data=TESTDATA)
        self.nex = self.maker.make()

    def test_languages(self):
        self.assertEqual(self.maker.languages, {'A', 'B', 'C', 'D'})

    def test_words(self):
        self.assertEqual(self.maker.words, {'eye', 'leg', 'arm'})

    def test_nsites(self):
        assert len(self.nex.data.keys()) == 6

    def test_cognate_sets(self):
        assert ('eye', '1') in self.maker.cognates
        assert ('leg', '1') in self.maker.cognates
        assert ('leg', '2') in self.maker.cognates
        assert ('arm', '1') in self.maker.cognates
        assert ('arm', '2') in self.maker.cognates
        assert ('arm', '3') in self.maker.cognates

    def test_is_missing_for_word(self):
        assert self.maker._is_missing_for_word('A', 'eye') == False
        assert self.maker._is_missing_for_word('A', 'leg') == False
        assert self.maker._is_missing_for_word('A', 'arm') == False

        assert self.maker._is_missing_for_word('B', 'eye') == False
        assert self.maker._is_missing_for_word('B', 'leg') == False
        assert self.maker._is_missing_for_word('B', 'arm') == False

        assert self.maker._is_missing_for_word('C', 'eye') == False
        assert self.maker._is_missing_for_word('C', 'leg') == True, "Should be missing 'leg' for Language 'C'"
        assert self.maker._is_missing_for_word('C', 'arm') == False

        assert self.maker._is_missing_for_word('D', 'eye') == True, "Should be missing 'eye' for Language 'D' (loan)"
        assert self.maker._is_missing_for_word('D', 'leg') == False
        assert self.maker._is_missing_for_word('D', 'arm') == False

    def test_eye_1(self):
        cog = 'eye_1'
        assert self.nex.data[cog]['A'] == '1'
        assert self.nex.data[cog]['B'] == '1'
        assert self.nex.data[cog]['C'] == '1'
        assert self.nex.data[cog]['D'] == '?'

    def test_leg_1(self):
        cog = 'leg_1'
        assert self.nex.data[cog]['A'] == '1'
        assert self.nex.data[cog]['B'] == '0'
        assert self.nex.data[cog]['C'] == '?'
        assert self.nex.data[cog]['D'] == '1'

    def test_leg_2(self):
        cog = 'leg_2'
        assert self.nex.data[cog]['A'] == '0'
        assert self.nex.data[cog]['B'] == '1'
        assert self.nex.data[cog]['C'] == '?'
        assert self.nex.data[cog]['D'] == '1'

    def test_arm_1(self):
        cog = 'arm_1'
        assert self.nex.data[cog]['A'] == '1'
        assert self.nex.data[cog]['B'] == '0'
        assert self.nex.data[cog]['C'] == '0'
        assert self.nex.data[cog]['D'] == '0'

    def test_arm_2(self):
        cog = 'arm_2'
        assert self.nex.data[cog]['A'] == '0'
        assert self.nex.data[cog]['B'] == '1'
        assert self.nex.data[cog]['C'] == '0'
        assert self.nex.data[cog]['D'] == '1'

    def test_arm_3(self):
        cog = 'arm_3'
        assert self.nex.data[cog]['A'] == '0'
        assert self.nex.data[cog]['B'] == '0'
        assert self.nex.data[cog]['C'] == '1'
        assert self.nex.data[cog]['D'] == '1'

    def test_write(self):
        out = self.maker.write()
        assert out.startswith("#NEXUS")
        assert 'NTAX=4' in out
        assert 'CHARSTATELABELS' in out
        assert 'MATRIX' in out


class TestNexusMakerAscertained(TestNexusMaker):
    def setUp(self):  # override parent method
        self.maker = NexusMakerAscertained(data=TESTDATA)
        self.nex = self.maker.make()

    # 1 more site than before in ascertainment = none
    def test_nsites(self):
        assert len(self.nex.data.keys()) == 7

    def test_ascertainment_column(self):
        assert self.maker.ASCERTAINMENT_LABEL in self.nex.data
        for k in self.nex.data[self.maker.ASCERTAINMENT_LABEL]:
            assert self.nex.data[self.maker.ASCERTAINMENT_LABEL][k] == '0'

    def test_error_on_multiple_ascertainment_sites(self):
        with self.assertRaises(ValueError):
            self.maker._add_ascertainment(self.nex)
