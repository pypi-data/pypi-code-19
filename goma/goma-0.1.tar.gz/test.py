# -*- coding: utf-8 -*-

#  goma
#  ----
#  General object mapping algorithm.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/goma
#  License: APACHE Version 2 License (see LICENSE file)


import os
import unittest
from goma import ExactMatch, PriorityMatch

from datetime import datetime, date, timedelta

class ExactMatchUnitTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_match(self):
        exact_match = ExactMatch()

        detail_list = [["Property1","Value1_2"],["Property2","Value2_2"],["Property3","Value3_2"]]
        mapping_list = [["Property1","Property2","Property3","Target"], \
                        ["Value1_1","Value2_1","Value3_1","Target1"], \
                        ["Value1_2","Value2_2","Value3_2","Target2"]]

        result = exact_match.match(detail_list, mapping_list)
        self.assertEqual("Target2",result, "Mapping algorithm not set up properly.")

class PriorityMatchUnitTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_match(self):
        priority_match = PriorityMatch()

        detail_list = [["Property1","Value1_2"],["Property2","Value2_1"],["Property3","Value3_3"]]
        mapping_list = [["Property1","Property2","Property3","Target"], \
                        ["Value1_1","","Value3_1","Target1"], \
                        ["Value1_1","","Value3_2","Target2"], \
                        ["","Value2_1","Value3_3","Target3"], \
                        ["","Value2_1","Value3_4","Target4"]]

        result = priority_match.match(detail_list, mapping_list)
        self.assertEqual("Target3",result, "Mapping algorithm not set up properly.")

if __name__ == "__main__":

    import sys
    start_time = datetime.now()

    print('')
    print('======================================================================')
    print('')
    print('run %s' % __file__)
    print('in %s' % os.getcwd())
    print('started  at %s' % str(start_time))
    print('')
    print('----------------------------------------------------------------------')
    print('')

    suite = unittest.TestLoader().loadTestsFromModule(__import__("__main__"))
    testrunner = unittest.TextTestRunner(stream=sys.stdout, descriptions=2, verbosity=2)
    testrunner.run(suite)

    print('')
    print('======================================================================')
    print('')
    print('ran %s' % __file__)
    print('in %s' % os.getcwd())
    print('started  at %s' % str(start_time))
    print('finished at %s' % str(datetime.now()))
    print('')
    print('----------------------------------------------------------------------')
    print('')
