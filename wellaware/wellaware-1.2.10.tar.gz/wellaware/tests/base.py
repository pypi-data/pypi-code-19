from __future__ import unicode_literals
import json
import logging
from mock import Mock, patch
from nose.tools import nottest
from nose.plugins.attrib import attr
import responses
from unittest import TestCase

from wellaware.constants import Config


logging.basicConfig(level=logging.DEBUG)

WA_ADMIN_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhdXRoMHwxMjM0NTY3ODkwIiwiem9uZWluZm8iOiJBbWVyaWNhL' \
                 '0NoaWNhZ28iLCJ3c3RrIjpudWxsLCJpc3MiOiJodHRwczovL3dlbGxhd2FyZS5hdXRoMC5jb20vIiwidG5hbWUiOiJXZWxsQXd' \
                 'hcmUiLCJnaXZlbl9uYW1lIjoiQWRtaW4iLCJ0aWQiOjE0OTQ4MDAwNCwic2lkIjoyNDgyOTI0MDc2LCJhdWQiOiJqelFyTEhBN' \
                 'TBYVGgxOHp3YlRnNmhSdllTV2dCdjQwSyIsInR1dWlkIjoiMDRiN2JkZDItMjE5Yy00MzdlLWExMTMtYzIyNTM0MjUxMzRhIiw' \
                 'iaW1wciI6bnVsbCwicmxzIjoiVXNlcixXZWxsQXdhcmUtU2VydmljZSxXZWxsQXdhcmUtQWRtaW4sV2VsbEF3YXJlLVNlcml2Y' \
                 '2UsQWRtaW4sQ29udHJvbGxlciIsImV4cCI6MTQ4OTYxNjExOSwicHJtcyI6Iio6KjoqLHRva2VucyxyZXZlcnNlTG9va3VwOnJ' \
                 'ldHJpZXZlLGltcGVyc29uYXRlOiosKjpyZXRyaWV2ZToqIiwiaWF0IjoxNDg5MTc0ODkzLCJmYW1pbHlfbmFtZSI6IldlbGxBd' \
                 '2FyZSIsImVtYWlsIjoiYWRtaW5Ad2VsbGF3YXJlLnVzIiwidXNlcm5hbWUiOiJhZG1pbkB3ZWxsYXdhcmUudXMifQ.mq50wniZ' \
                 'G4zzYMcUOrcVJEGXb25om8nxysg0ATFdfA4'


class BaseClientTestCase(TestCase):
    """
    Adds utility methods.
    """

    @classmethod
    def setUpClass(cls):
        Config.base_url = 'http://localhost'
        Config.timeout = 1
        Config.include_token = True
        super(BaseClientTestCase, cls).setUpClass()

    def assertHasAttr(self, obj, attr):
        self.assertTrue(hasattr(obj, attr), "%s doesn't have attribute: %s" % (obj, attr))

    def assertNotHasAttr(self, obj, attr):
        self.assertFalse(hasattr(obj, attr), "%s shouldn't have attribute: %s" % (obj, attr))

    def assertAttrEqual(self, obj, attr, value):
        self.assertHasAttr(obj, attr)
        self.assertEqual(getattr(obj, attr), value)

    def assertAttrNotEqual(self, obj, attr, value):
        self.assertHasAttr(obj, attr)
        self.assertNotEqual(getattr(obj, attr), value)

    def assertNotRaise(self, callableObj, *args, **kwargs):
        try:
            callableObj(*args, **kwargs)
        except Exception as e:
            raise AssertionError("Shouldn't raise and exception: {}".format(e))

    def assertAnyRaise(self, callableObj, *args, **kwargs):
        try:
            callableObj(*args, **kwargs)
        except:
            return
        raise AssertionError("Should raise an exception")

    def assertIsSubclass(self, C, B):
        if issubclass(C, B):
            return
        else:
            raise AssertionError("{} is Not a Subclass of {}".format(B, C))

    def assertDictContainsKey(self, obj, key):
        if key in obj:
            return
        else:
            raise AssertionError("{} is not in dict: {}".format(key, obj))

    def assertDictContainsKeyWithValue(self, obj, key, value):
        if key in obj:
            self.assertEquals(value, obj[key])
        else:
            raise AssertionError("{} is not in dict: {}".format(key, obj))

    def assertDictContainsKeyWithValueType(self, obj, key, B):
        if key in obj:
            if isinstance(obj[key], B):
                return
            else:
                raise AssertionError("dict[{}]={} is not of type: {}".format(key, obj[key], B))
        else:
            raise AssertionError("{} is not in dict: {}".format(key, obj))


__all__ = ['BaseClientTestCase', 'nottest', 'attr', 'json', 'Mock', 'patch', 'responses', 'WA_ADMIN_TOKEN']
