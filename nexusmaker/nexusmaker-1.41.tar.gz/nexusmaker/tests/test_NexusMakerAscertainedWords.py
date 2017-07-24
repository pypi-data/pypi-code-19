import sys
import unittest

from nexusmaker import NexusMakerAscertainedWords
from .test_NexusMaker import TestNexusMaker, TESTDATA

class Test_Is_Sequential(unittest.TestCase):
    def setUp(self):
        self.maker = NexusMakerAscertainedWords([])
    
    def test_true(self):
        assert self.maker._is_sequential([1,2,3,4,5])

    def test_true_2(self):
        assert self.maker._is_sequential([3,4,5,6,7])

    def test_false(self):
        assert not self.maker._is_sequential([1, 3])


class TestNexusMakerAscertainedWords(TestNexusMaker):
    
    def setUp(self):  # override parent method
        self.maker = NexusMakerAscertainedWords(data=TESTDATA)
        self.nex = self.maker.make()

    def test_get_characters_simple(self):
        chars = self.maker._get_characters(self.nex)
        # NOTE characters are zero indexed
        assert chars['arm'] == [0, 1, 2, 3]
        assert chars['eye'] == [4, 5]
        assert chars['leg'] == [6, 7, 8]
    
    def test_get_characters_error(self):
        with self.assertRaises(ValueError):
            chars = self.maker._get_characters(self.nex, delimiter="X")

    def test_create_assumptions_simple(self):
        assumpt = self.maker.create_assumptions(self.nex)
        assert 'begin assumptions' in assumpt[0]
        assert 'arm = 1-4' in assumpt[1]
        assert 'eye = 5-6' in assumpt[2]
        assert 'leg = 7-9' in assumpt[3]
        assert 'end;' in assumpt[4]
    
    # 1 more site per word than in ascertainment = none, = 6 cognates + 3 words = 9
    def test_nsites(self):
        assert len(self.nex.data.keys()) == 9
    
    def test_eye_0(self):
        cog = 'eye_%s' % self.maker.ASCERTAINMENT_LABEL
        assert self.nex.data[cog]['A'] == '0'
        assert self.nex.data[cog]['B'] == '0'
        assert self.nex.data[cog]['C'] == '0'
        assert self.nex.data[cog]['D'] == '?'

    def test_leg_0(self):
        cog = 'leg_%s' % self.maker.ASCERTAINMENT_LABEL
        assert self.nex.data[cog]['A'] == '0'
        assert self.nex.data[cog]['B'] == '0'
        assert self.nex.data[cog]['C'] == '?'
        assert self.nex.data[cog]['D'] == '0'

    def test_arm_0(self):
        cog = 'arm_%s' % self.maker.ASCERTAINMENT_LABEL
        assert self.nex.data[cog]['A'] == '0'
        assert self.nex.data[cog]['B'] == '0'
        assert self.nex.data[cog]['C'] == '0'
        assert self.nex.data[cog]['D'] == '0'
    
    def test_write_extra(self):
        out = self.maker.write()
        assert 'begin assumptions;' in out
        assert 'charset arm' in out
        assert 'charset eye' in out
        assert 'charset leg' in out

