import unittest
import configparser
from hft.util import *
from hft.plot import *
from hft.portfolio import *
from hft.position import *
from hft.metric import *
    
class TestDocString(unittest.TestCase):
             
    def __init__(self, *args, **kwargs):
        config = configparser.ConfigParser()
        config.read('credentials.ini')
           
        util_setCredentials(config['DEFAULT']['username'],
                                config['DEFAULT']['password'],
                                config['DEFAULT']['apiKey'])
        super(TestDocString, self).__init__(*args, **kwargs)
           
    def test_portfolio(self):
        portfolio = Portfolio('t-1', 't', 'SPY')
        assert   len(Portfolio.__init__.__doc__)>0
        assert   len(portfolio.settings.__doc__)>0
        assert   len(portfolio.symbols.__doc__)>0
           
    def test_position(self):
        portfolio = Portfolio('t-1', 't', 'SPY')
        positionAAPL = portfolio.add_position( 'AAPL', 100)
        assert   len(positionAAPL.profit.__doc__)>0   
        assert   len(positionAAPL.beta.__doc__)>0
        assert   len(positionAAPL.alpha_exante.__doc__)>0
        assert   len(positionAAPL.variance.__doc__)>0   
        assert   len(positionAAPL.max_drawdown.__doc__)>0   
        assert   len(positionAAPL.calmar_ratio.__doc__)>0   
        assert   len(positionAAPL.value_at_risk.__doc__)>0   
        assert   len(positionAAPL.expected_shortfall.__doc__)>0   
        assert   len(positionAAPL.mod_sharpe_ratio.__doc__)>0
        assert   len(positionAAPL.log_return.__doc__)>0   
           
        #print(positionAAPL.log_return.__doc__)
                      
    if __name__ == '__main__':
        unittest.main()
