import unittest
import configparser
from hft.util import *
from hft.plot import *
from hft.portfolio import *
from hft.position import *
from hft.metric import *


class TestMetricMath(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        config = configparser.ConfigParser()
        config.read('credentials.ini')

        util_setCredentials(config['DEFAULT']['username'],
                            config['DEFAULT']['password'],
                            config['DEFAULT']['apiKey'])
        super(TestMetricMath, self).__init__(*args, **kwargs)

    def test_add_int(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        variance = compute(portfolio.variance())
        new_variance=compute(portfolio.variance()+1)
        assert new_variance[0][1][1]==variance[0][1][1]+1

    def test_add(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        varianceG = compute(positionG.variance())
        varianceA = compute(positionA.variance())
        new_variance=compute(positionG.variance()+positionA.variance())
        assert new_variance[0][1][1]==varianceG[0][1][1]+varianceA[0][1][1]

    def test_radd_int(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        variance = compute(portfolio.variance())
        new_variance = compute(1+portfolio.variance())
        assert new_variance[0][1][1] == variance[0][1][1] + 1

    def test_radd(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        varianceG = compute(positionG.variance())
        varianceA = compute(positionA.variance())
        new_variance = compute(positionA.variance()+ positionG.variance())
        assert new_variance[0][1][1] == varianceG[0][1][1] + varianceA[0][1][1]

    def test_sub_int(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        variance = compute(portfolio.variance())
        new_variance=compute(portfolio.variance()-1)
        assert new_variance[0][1][1]==variance[0][1][1]-1

    def test_sub(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        varianceG = compute(positionG.variance())
        varianceA = compute(positionA.variance())
        new_variance=compute(positionG.variance()-positionA.variance())
        assert new_variance[0][1][1]==varianceG[0][1][1]-varianceA[0][1][1]

    def test_rsub_int(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        variance = compute(portfolio.variance())
        new_variance = compute(1-portfolio.variance())
        assert new_variance[0][1][1] == 1-variance[0][1][1]

    def test_rsub(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        varianceG = compute(positionG.variance())
        varianceA = compute(positionA.variance())
        new_variance = compute(positionA.variance()- positionG.variance())
        assert new_variance[0][1][1] == varianceA[0][1][1] - varianceG[0][1][1]

    def test_mul_int(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        variance = compute(portfolio.variance())
        new_variance=compute(portfolio.variance()*2)
        assert new_variance[0][1][1]==variance[0][1][1]*2

    def test_mul(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        varianceG = compute(positionG.variance())
        varianceA = compute(positionA.variance())
        new_variance=compute(positionG.variance()*positionA.variance())
        assert new_variance[0][1][1]==varianceG[0][1][1]*varianceA[0][1][1]

    def test_rmul_int(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        variance = compute(portfolio.variance())
        new_variance = compute(2*portfolio.variance())
        assert new_variance[0][1][1] == variance[0][1][1]*2

    def test_rmul(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        varianceG = compute(positionG.variance())
        varianceA = compute(positionA.variance())
        new_variance = compute(positionA.variance()*positionG.variance())
        assert new_variance[0][1][1] == varianceG[0][1][1]*varianceA[0][1][1]

    def test_truediv_int(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        variance = compute(portfolio.variance())
        new_variance=compute(portfolio.variance()/2)
        assert new_variance[0][1][1]==variance[0][1][1]/2

    def test_truediv(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        varianceG = compute(positionG.variance())
        varianceA = compute(positionA.variance())
        new_variance=compute(positionG.variance()/positionA.variance())
        assert new_variance[0][1][1]==varianceG[0][1][1]/varianceA[0][1][1]

    def test_rtruediv_int(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        variance = compute(portfolio.variance())
        new_variance = compute(2/portfolio.variance())
        assert new_variance[0][1][1] == 2/variance[0][1][1]

    def test_rtruediv(self):
        portfolio = Portfolio('2015-06-12 09:30:00', '2015-06-14 16:00:00', 'SPY')
        positionG = portfolio.add_position('GOOG', 100)
        positionA = portfolio.add_position('AAPL', 100)
        varianceG = compute(positionG.variance())
        varianceA = compute(positionA.variance())
        new_variance = compute(positionA.variance()/positionG.variance())
        assert new_variance[0][1][1] == varianceA[0][1][1]/varianceG[0][1][1]

if __name__ == '__main__':
    unittest.main()
