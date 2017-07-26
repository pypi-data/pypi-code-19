from opfront.model import Model
from opfront.user import UserResource

from unittest.mock import MagicMock


import unittest

VALID_USER_BODY = {
    'email': 'hello@world.ca',
    'is_admin': False
}


class MockClient(object):

    def __init__(self, request):
        self.do_request = request


class TestGetMe(unittest.TestCase):

    def test_me_calls_correct_url(self):
        mock_client = MockClient(MagicMock(return_value=VALID_USER_BODY))

        u = UserResource('/users', mock_client)
        u.me()

        self.assertTrue(mock_client.do_request.called)
        self.assertEqual(mock_client.do_request.call_args[0][0], '/users/me')

    def test_me_uses_correct_http_method(self):
        mock_client = MockClient(MagicMock(return_value=VALID_USER_BODY))

        u = UserResource('/users', mock_client)
        u.me()

        self.assertTrue(mock_client.do_request.called)
        self.assertEqual(mock_client.do_request.call_args[0][1], 'GET')

    def test_me_returns_generic_model_from_response(self):
        mock_client = MockClient(MagicMock(return_value=VALID_USER_BODY))

        u = UserResource('/users', mock_client)
        user = u.me()

        self.assertIsInstance(user, Model)

        for k, v in VALID_USER_BODY.items():
            self.assertEqual(getattr(user, k), v)
