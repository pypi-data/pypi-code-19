import datetime
import os
import time 
import unittest

import numpy
import cf

class functionsTest(unittest.TestCase):
    def test_boolean_constants(self):
        for f in ('REGRID_LOGGING',
#                'IGNORE_IDENTITIES',
                #                  'RELAXED_IDENTITIES',
                  ):
            func = getattr(cf, f) 
            x = func(False)
            org = func()
            self.assertTrue(org is False)
            self.assertTrue(func(True) is False)
            self.assertTrue(func() is True)
            self.assertTrue(func(org) is True)
            self.assertTrue(func() is False)
            func(x)
    #--- End: def
#--- End: class


if __name__ == '__main__':
    print 'Run date:', datetime.datetime.utcnow()
    cf.environment()
    print
    unittest.main(verbosity=2)
