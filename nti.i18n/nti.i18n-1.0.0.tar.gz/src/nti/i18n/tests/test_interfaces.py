# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

import unittest

class TestInterfaces(unittest.TestCase):

    def test_imports(self):
        from nti.i18n import interfaces
        self.assertIsNotNone(interfaces)
