from mock import patch
from unittest import TestCase
from mock import patch, MagicMock

from test.helpers.test_util import TestUtil
from hudai.resource import Resource


class TestResource(TestCase):
    def test_resource(self):
        resource = Resource(TestUtil.get_key())
        self.assertIsInstance(resource, Resource)
        self.assertTrue(resource.make_request)
        self.assertTrue(resource.build_url)

    def test_build_url(self):
        resource = Resource(TestUtil.get_key())
        url = resource.build_url({
            'method': 'GET',
            'params': {'id': 1},
            'url': '/test/{id}'
        })

        self.assertEqual(url, '/test/1')