from opfront.client import OpfrontClient
from opfront.exceptions import BadRequestError, IntegrityError, ResourceNotFoundError, UnexpectedError, ForbiddenError

from unittest.mock import MagicMock, patch

import unittest

AUTH_TOKEN = 'asdf'
REFRESH_TOKEN = 'hjkl'

AUTH_BODY = {
    'auth_token': AUTH_TOKEN,
    'refresh_token': REFRESH_TOKEN
}

SOME_BODY = {
    'once': 'told',
    'me': {
        'the': 'world',
        'is': 'gonna',
        'roll': 'me'
    }
}

EMAIL = "hello@wor.ld"
PASSWORD = "p455w0rd"
URL = '/endpoint'


class Response(object):

    def __init__(self, resp={}, status_code=200):
        self._resp = resp
        self.status_code = status_code

    def json(self):
        return {
            'data': self._resp
        }


class TestClient(unittest.TestCase):

    def test_client_calls_auth_to_get_token(self):
        mock_post = MagicMock(return_value=Response(AUTH_BODY))
        with patch('opfront.client.requests.post', mock_post):
            OpfrontClient(EMAIL, PASSWORD)

        self.assertTrue(mock_post.called)
        self.assertEqual(mock_post.call_count, 1)

    def test_client_sets_tokens_after_response(self):
        mock_post = MagicMock(return_value=Response(AUTH_BODY))
        with patch('opfront.client.requests.post', mock_post):
            c = OpfrontClient(EMAIL, PASSWORD)
            self.assertEqual(c._token, AUTH_TOKEN)
            self.assertEqual(c._refresh, REFRESH_TOKEN)


class TestClientDoRequest(unittest.TestCase):

    def setUp(self):
        mock_post = MagicMock(return_value=Response(AUTH_BODY))
        with patch('opfront.client.requests.post', mock_post):
            self.client = OpfrontClient(EMAIL, PASSWORD)

    def test_client_do_request_calls_get_when_get_request(self):
        mock_get = MagicMock(return_value=Response(SOME_BODY))
        with patch('opfront.client.requests.get', mock_get):
            self.client.do_request(URL, 'GET')

        self.assertTrue(mock_get.called)
        self.assertEqual(mock_get.call_count, 1)

    def test_client_do_request_calls_post_when_post_request(self):
        mock_post = MagicMock(return_value=Response(SOME_BODY))
        with patch('opfront.client.requests.post', mock_post):
            self.client.do_request(URL, 'POST')

        self.assertTrue(mock_post.called)
        self.assertTrue(mock_post.call_count, 1)

    def test_client_do_request_calls_put_when_put_request(self):
        mock_put = MagicMock(return_value=Response(SOME_BODY))
        with patch('opfront.client.requests.put', mock_put):
            self.client.do_request(URL, 'PUT')

        self.assertTrue(mock_put.called)
        self.assertEqual(mock_put.call_count, 1)

    def test_client_do_request_calls_delete_when_delete_request(self):
        mock_del = MagicMock(return_value=Response(SOME_BODY))
        with patch('opfront.client.requests.delete', mock_del):
            self.client.do_request(URL, 'DELETE')

        self.assertTrue(mock_del.called)
        self.assertEqual(mock_del.call_count, 1)

    def test_client_do_request_raises_value_error_on_invalid_http_method(self):
        with self.assertRaises(ValueError):
            self.client.do_request(URL, 'HJKL')

    def test_client_do_request_returns_none_when_status_is_204(self):
        mock_del = MagicMock(return_value=Response(status_code=204))
        with patch('opfront.client.requests.delete', mock_del):
            r = self.client.do_request(URL, 'DELETE')

        self.assertIsNone(r)

    def test_client_do_request_raises_resource_not_found_on_404(self):
        mock_get = MagicMock(return_value=Response(status_code=404))
        with patch('opfront.client.requests.get', mock_get):
            with self.assertRaises(ResourceNotFoundError):
                self.client.do_request(URL, 'GET')

    def test_client_do_request_raises_bad_request_on_400(self):
        mock_post = MagicMock(return_value=Response(status_code=400))
        with patch('opfront.client.requests.post', mock_post):
            with self.assertRaises(BadRequestError):
                self.client.do_request(URL, 'POST')

    def test_client_do_request_raises_integrity_error_on_422(self):
        mock_post = MagicMock(return_value=Response(status_code=422))
        with patch('opfront.client.requests.post', mock_post):
            with self.assertRaises(IntegrityError):
                self.client.do_request(URL, 'POST')

    def test_client_do_request_raises_unexpected_error_on_500(self):
        mock_get = MagicMock(return_value=Response(status_code=500))
        with patch('opfront.client.requests.get', mock_get):
            with self.assertRaises(UnexpectedError):
                self.client.do_request(URL, 'GET')

    def test_client_do_request_raises_forbidden_on_403(self):
        mock_get = MagicMock(return_value=Response(status_code=403))
        with patch('opfront.client.requests.get', mock_get), self.assertRaises(ForbiddenError):
            self.client.do_request(URL, 'GET')
