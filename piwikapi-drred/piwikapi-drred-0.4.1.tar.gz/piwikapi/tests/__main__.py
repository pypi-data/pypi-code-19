from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from analytics import AnalyticsClassTestCase
from analytics import AnalyticsTestCase
from analytics import AnalyticsLiveTestCase
from ecommerce import TrackerEcommerceVerifyTestCase
from goals import GoalsTestCase
from tracking import TrackerClassTestCase
from tracking import TrackerVerifyDebugTestCase
from tracking import TrackerVerifyTestCase


if __name__ == '__main__':
    unittest.main()
