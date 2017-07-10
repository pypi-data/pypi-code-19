import unittest

from aloe.plotter import tokenizer

programs = [
    'x(q(r(s,s)),q(l,l))y(a,b,c(h,j))z(a,b)',
    'block(elem(mod,mod))'
]

class TestTokenizer(unittest.TestCase):
    def test_inverse(self):
        for production in programs:
            reproduced = ''

            t = tokenizer(production)
            while not t.empty():
                reproduced += t.next()

            self.assertEqual(production, reproduced)

if __name__ == '__main__':
    unittest.main()
