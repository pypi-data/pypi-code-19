from unittest import TestCase
from admanagerplusclient import ampclient

class TestBrightRollClient(TestCase):
    def test_config(self):
        b = ampclient.BrightRollClient()
        self.assertTrue(isinstance(b, ampclient.BrightRollClient))

