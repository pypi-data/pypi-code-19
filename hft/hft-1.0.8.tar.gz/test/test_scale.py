import unittest
import configparser
from hft.util import *
from hft.plot import *
from hft.portfolio import *
from hft.position import *
from hft.metric import *

class TestAddpositionMethods(unittest.TestCase):
         
    def __init__(self, *args, **kwargs):
        config = configparser.ConfigParser()
        config.read('credentials.ini')
        
        util_setCredentials(config['DEFAULT']['username'], 
                            config['DEFAULT']['password'], 
                            config['DEFAULT']['apiKey'])
        super(TestAddpositionMethods, self).__init__(*args, **kwargs)
        
    def test_addSingleQuantity(self):
        portfolio_1 = Portfolio('t-1', 't', 'SPY')
        positionG_1 = portfolio_1.add_position('GOOG', 100)
        positionA_1 = portfolio_1.add_position('AAPL', 100)
        
        portfolio_2 = Portfolio('t-3', 't', 'SPY')
        positionG_2 = portfolio_2.add_position('GOOG', 100)
        positionA_2 = portfolio_2.add_position('AAPL', 100)
        
        util_plot(portfolio_2.variance(),portfolio_1.variance())
        #assert   len(Variance[0][0])>0


   
 
if __name__ == '__main__':
    unittest.main()
