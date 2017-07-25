from opfront.exceptions import ResourceNotFoundError
from opfront.model import Model
from opfront.resource import OpfrontResource

from unittest.mock import MagicMock, patch


import types
import unittest


ENDPOINT = "/res"
RES_ID = 18

ATTRIBUTE_SET = {
    'hello': 'world',
    'order': 66,
    'test': True,
    'and then there were': None,
    'id': RES_ID
}

TOTAL_LIST_HITS = 20
PAGE_SIZE = 2

LIST_BODY = {
    'hits': [ATTRIBUTE_SET, ATTRIBUTE_SET],
    'total': TOTAL_LIST_HITS
}


class MockClient(object):

    def __init__(self, response={}, should_raise=None):

        if should_raise is not None:
            self.do_request = MagicMock(side_effect=should_raise)

        else:
            self.do_request = MagicMock(return_value=response)


class TestResourceCall(unittest.TestCase):

    def test_resource_call_returns_model(self):
        res = OpfrontResource(ENDPOINT, MockClient())
        m = res(**ATTRIBUTE_SET)

        self.assertIsInstance(m, Model)

    def test_resource_call_passes_self_to_model(self):
        res = OpfrontResource(ENDPOINT, MockClient())
        m = res(**ATTRIBUTE_SET)

        self.assertIs(m._res, res)

    def test_resource_passes_attributes_to_model(self):
        res = OpfrontResource(ENDPOINT, MockClient())
        m = res(**ATTRIBUTE_SET)

        for k, v in ATTRIBUTE_SET.items():
            self.assertEqual(getattr(m, k), v)


class TestResourceGet(unittest.TestCase):

    def test_resource_get_calls_do_request(self):
        client = MockClient()
        res = OpfrontResource(ENDPOINT, client)

        res.get(RES_ID)

        self.assertTrue(client.do_request.called)
        self.assertEqual(client.do_request.call_count, 1)

    def test_resource_get_calls_do_request_with_http_get(self):
        client = MockClient()
        res = OpfrontResource(ENDPOINT, client)

        res.get(RES_ID)

        self.assertEqual(client.do_request.call_args[0][1], 'GET')

    def test_resource_get_appends_id_to_endpoint(self):
        client = MockClient()
        res = OpfrontResource(ENDPOINT, client)

        res.get(RES_ID)

        self.assertEqual(client.do_request.call_args[0][0], '{0}/{1}'.format(ENDPOINT, RES_ID))

    def test_resource_get_returns_model_instance(self):
        client = MockClient()
        res = OpfrontResource(ENDPOINT, client)

        m = res.get(RES_ID)

        self.assertIsInstance(m, Model)

    def test_resource_get_returns_model_with_response_attributes(self):
        client = MockClient(response=ATTRIBUTE_SET)
        res = OpfrontResource(ENDPOINT, client)

        m = res.get(RES_ID)

        for k, v in ATTRIBUTE_SET.items():
            self.assertEqual(getattr(m, k), v)


class TestResourceExists(unittest.TestCase):

    @patch('opfront.resource.OpfrontResource.get', MagicMock())
    def test_resource_exists_returns_true_when_no_exception_is_raised(self):
        client = MockClient(response=ATTRIBUTE_SET)
        res = OpfrontResource(ENDPOINT, client)

        self.assertTrue(res.exists(RES_ID))

    def test_resource_exists_returns_false_when_resource_not_found_is_raised(self):
        client = MockClient(should_raise=ResourceNotFoundError)
        res = OpfrontResource(ENDPOINT, client)

        self.assertFalse(res.exists(RES_ID))

    @patch('opfront.resource.OpfrontResource.get', MagicMock(side_effect=ValueError))
    def test_resource_exists_reraises_other_exceptions(self):
        client = MockClient(response=ATTRIBUTE_SET)
        res = OpfrontResource(ENDPOINT, client)

        with self.assertRaises(ValueError):
            res.exists(RES_ID)


class TestResourceList(unittest.TestCase):

    def test_resource_list_returns_a_generator(self):
        client = MockClient(response=LIST_BODY)
        res = OpfrontResource(ENDPOINT, client)

        hits = res.list()

        self.assertIsInstance(hits, types.GeneratorType)

    def test_resource_list_returns_correct_item_count(self):
        client = MockClient(response=LIST_BODY)
        res = OpfrontResource(ENDPOINT, client)

        hits = [hit for hit in res.list(page_size=PAGE_SIZE)]

        self.assertEqual(len(hits), TOTAL_LIST_HITS)

    def test_resource_list_perform_correct_number_of_request(self):
        client = MockClient(response=LIST_BODY)
        res = OpfrontResource(ENDPOINT, client)

        hits = [hit for hit in res.list(page_size=PAGE_SIZE)]

        self.assertEqual(client.do_request.call_count, TOTAL_LIST_HITS / PAGE_SIZE)


class TestResourceCreate(unittest.TestCase):

    def test_resource_create_calls_do_request(self):
        client = MockClient(response=ATTRIBUTE_SET)
        res = OpfrontResource(ENDPOINT, client)

        res.create(Model(res, **ATTRIBUTE_SET))

        self.assertTrue(client.do_request.called)
        self.assertEqual(client.do_request.call_count, 1)

    def test_resource_create_does_post_request(self):
        client = MockClient(response=ATTRIBUTE_SET)
        res = OpfrontResource(ENDPOINT, client)

        res.create(Model(res, **ATTRIBUTE_SET))

        self.assertEqual(client.do_request.call_args[0][1], 'POST')

    def test_resource_create_does_not_append_to_url(self):
        client = MockClient(response=ATTRIBUTE_SET)
        res = OpfrontResource(ENDPOINT, client)

        res.create(Model(res, **ATTRIBUTE_SET))

        self.assertEqual(client.do_request.call_args[0][0], ENDPOINT)

    def test_resource_create_returns_model_instance(self):
        client = MockClient(response=ATTRIBUTE_SET)
        res = OpfrontResource(ENDPOINT, client)

        m = res.create(Model(res, **ATTRIBUTE_SET))

        self.assertIsInstance(m, Model)


class TestResourceUpdate(unittest.TestCase):

    def test_resource_update_calls_do_request(self):
        client = MockClient(response=ATTRIBUTE_SET)
        res = OpfrontResource(ENDPOINT, client)

        res.update(Model(res, **ATTRIBUTE_SET))

        self.assertTrue(client.do_request.called)
        self.assertEqual(client.do_request.call_count, 1)

    def test_resource_update_does_put_request(self):
        client = MockClient(response=ATTRIBUTE_SET)
        res = OpfrontResource(ENDPOINT, client)

        res.update(Model(res, **ATTRIBUTE_SET))

        self.assertEqual(client.do_request.call_args[0][1], 'PUT')

    def test_resource_update_appends_id_to_url(self):
        client = MockClient(response=ATTRIBUTE_SET)
        res = OpfrontResource(ENDPOINT, client)

        res.update(Model(res, **ATTRIBUTE_SET))

        self.assertEqual(client.do_request.call_args[0][0], '{0}/{1}'.format(ENDPOINT, RES_ID))

    def test_resource_update_returns_model_instance(self):
        client = MockClient(response=ATTRIBUTE_SET)
        res = OpfrontResource(ENDPOINT, client)

        m = res.update(Model(res, **ATTRIBUTE_SET))

        self.assertIsInstance(m, Model)


class TestResourceDelete(unittest.TestCase):

    def test_resource_delete_calls_do_request(self):
        client = MockClient()
        res = OpfrontResource(ENDPOINT, client)

        res.delete(RES_ID)

        self.assertTrue(client.do_request.called)
        self.assertEqual(client.do_request.call_count, 1)

    def test_resource_delete_does_delete_request(self):
        client = MockClient()
        res = OpfrontResource(ENDPOINT, client)

        res.delete(RES_ID)

        self.assertEqual(client.do_request.call_args[0][1], 'DELETE')

    def test_resource_delete_appends_id_to_url(self):
        client = MockClient()
        res = OpfrontResource(ENDPOINT, client)

        res.delete(RES_ID)

        self.assertEqual(client.do_request.call_args[0][0], '{0}/{1}'.format(ENDPOINT, RES_ID))
