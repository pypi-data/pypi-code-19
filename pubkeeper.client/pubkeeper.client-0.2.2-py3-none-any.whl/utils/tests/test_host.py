from unittest import TestCase
from unittest.mock import patch

from pubkeeper.utils.host import Host


class TestHost(TestCase):

    def test_0_0_0_0(self):
        ip_address = "0.0.0.0"
        self.assertTrue(Host.is_valid(ip_address))

    def test_invalid_ip(self):
        # no chance of accepting a 900 octet
        ip_address = "10.0.0.900"
        self.assertFalse(Host.is_valid(ip_address))

    def test_availability_ip_not_valid(self):
        """ Asserts that method wait_for_ip_address returns False
        when timeout expires and ip has not become valid
        """
        with patch.object(Host, "is_valid", return_value=False):
            # assert no calls to sleep when timeout is 0
            with patch(Host.__module__ + ".sleep") as mocked_sleep:
                self.assertFalse(Host.wait_for_ip_address("irrelevant",
                                                          0, 0.1))
                self.assertEqual(mocked_sleep.call_count, 0)

            with patch(Host.__module__ + ".sleep") as mocked_sleep:
                self.assertFalse(Host.wait_for_ip_address("irrelevant",
                                                          0.001, 0.1))
                self.assertGreater(mocked_sleep.call_count, 0)

    def test_availability_ip_valid(self):
        """ Asserts that method wait_for_ip_address returns True
        when ip is valid
        """
        with patch.object(Host, "is_valid", return_value=True):
            # assert that waiting is over when ip is valid
            with patch(Host.__module__ + ".sleep") as mocked_sleep:
                self.assertTrue(Host.wait_for_ip_address("irrelevant",
                                                         0.001, 0.1))
                self.assertEqual(mocked_sleep.call_count, 1)
