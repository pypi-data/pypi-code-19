
# To run this, go to the project root (not this directory) and run:
#
# python -m unittest discover -s test

import unittest, json, re
from os.path import join, dirname

from jssourcemap import SourceMap
from jssourcemap.vlq import encode, decode


def _sortkey(token):
    return (token.genLine, token.genCol)


def readfile(name):
    path = dirname(__file__)
    return open(join(path, name)).read()


class TestVLQ(unittest.TestCase):
    def test_vlq(self):
        for (n, ch) in [
                (1, "C"),
                (-1, "D"),
                (2, "E"),
                (-2, "F"),
                (0, "A"),
                (16, "gB"),
                (948, "o7B"), ]:
            self.assertEqual(encode([n]), ch)
            self.assertEqual(decode(ch), [n])


class TestReproduce(unittest.TestCase):
    """
    Can we reproduce something we read in?
    """
    def test_a(self):
        self._testfile('a')

    def test_b(self):
        self._testfile('b')

    def test_both(self):
        self._testfile('both')

    def _testfile(self, prefix):
        content = readfile(prefix + '.min.js.map')
        original = json.loads(content)

        smap = SourceMap()
        smap.read(content)
        generated = smap.generate()

        # Start with the items we use to calculate mappings.  If they are off
        # then the rest is going to be wrong.

        self.assertEqual(original['sources'], generated['sources'])

        self.assertEqual(original['names'], generated['names'])

        r = re.compile(r'(;|,|[a-zA-Z0-9+\/]+)')
        lhs = [p for p in r.findall(original['mappings']) if p != ',']

        rhs = [p for p in r.findall(generated['mappings']) if p != ',']

        self.assertEqual(lhs, rhs)


class TestMerge(unittest.TestCase):

    # The a.js and b.js files were run through uglifyjs (with -b) to generate a
    # source map that matches the original source.  Then both were run through
    # uglifyjs at once to generate a combined source map.  I expect the source
    # map for both.js to match one we build from the a and b source maps.
    #
    # uglifyjs a.js -b --output a.min.js --source-map a.min.js.map
    # uglifyjs b.js -b --output b.min.js --source-map b.min.js.map
    # uglifyjs a.js b.js -b --output both.min.js --source-map both.min.js.map
    #
    # The "min.js" files are not needed - they should be identical to the
    # original source files except for the extra source mapping URL comment at
    # the bottom.

    def test_merge(self):
        # smap = SourceMap()

        path = dirname(__file__)

        # smap.read(open(join(path, 'a.min.js.map')).read())
        # smap.read(open(join(path, 'b.min.js.map')).read())

        both = SourceMap()
        both.read(open(join(path, 'both.min.js.map')).read())

        # # Compare the tokens.  If they are off the mappings are already off.

        # lhs = smap.tokens[:]
        # lhs.sort(key=_sortkey)

        # rhs = both.tokens[:]
        # lhs.sort(key=_sortkey)

        # self.assertEqual(len(lhs), len(rhs))

        # for l, r in zip(lhs, rhs):
        #     self.assertEqual(l, r)
