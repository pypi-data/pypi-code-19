from opfront.resource import OpfrontResource
from opfront.session import OpfrontSession

from unittest.mock import MagicMock, patch


import unittest


REQUIRED_RESOURCES = [
    'user',
    'spectacle',
    'store',
    'product',
    'order'
]

EMAIL = 'hello@wor.ld'
PASSWORD = 'p455w0rd'


class TestSession(unittest.TestCase):

    @patch('opfront.session.OpfrontClient', MagicMock)
    def test_session_defines_all_required_resources(self):
        s = OpfrontSession(EMAIL, PASSWORD)

        self.assertTrue(
            all([
                hasattr(s, res) and isinstance(getattr(s, res), OpfrontResource) for res in REQUIRED_RESOURCES
            ])
        )

    @patch('opfront.session.OpfrontClient', MagicMock)
    def test_session_also_works_as_a_context_manager(self):
        with OpfrontSession(EMAIL, PASSWORD) as s:
            self.assertTrue(
                all([
                    hasattr(s, res) and isinstance(getattr(s, res), OpfrontResource) for res in REQUIRED_RESOURCES
                ])
            )

