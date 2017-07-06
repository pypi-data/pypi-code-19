# Make a package

import unittest

def skipIfNoPlone(func):
    try:
        import plone.i18n
        return func
    except ImportError:
        return unittest.skip("plone.i18n not available")(func)
