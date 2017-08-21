import socket
from unittest import TestCase
from unittest.mock import patch, Mock

from pubkeeper.utils.port_manager import PortManager, PortNotAvailable, \
    InvalidIPAddress


class TestAvailablePort(TestCase):
    def setUp(self):
        self._test_settings = {
            'ip_address': '127.0.0.1',
            'port_manager_min_port': 7000,
            'port_manager_max_port': 7999,
            'connect_interval': 1,
            'connect_timeout': 0
        }

        self._port_manager = PortManager()
        self._port_manager.configure(self._test_settings)

    def test_available_port(self):
        """ This test checks that a port cannot be used until it is
        released
        """
        available_port = self._port_manager.reserve_port()
        port = available_port.get()

        self.assertGreaterEqual(port,
                                self._test_settings['port_manager_min_port'])
        self.assertLessEqual(port,
                             self._test_settings['port_manager_max_port'])

        # make sure it is not possible to bind to this port
        # unless it is released
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with self.assertRaises(OSError):
            s.bind((self._test_settings['ip_address'], port))

        # release port
        self._port_manager.release_reserved_port(available_port)
        # now it is ok to bind to port
        s.bind((self._test_settings['ip_address'], port))
        s.close()

    def test_immediate_available_ports(self):
        """ This test checks that a port is available right away
        when using "get_available_port"
        """
        port = self._port_manager.get_port()

        self.assertGreaterEqual(port,
                                self._test_settings['port_manager_min_port'])
        self.assertLessEqual(port,
                             self._test_settings['port_manager_max_port'])

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self._test_settings['ip_address'], port))
        s.close()
        self.assertGreaterEqual(port,
                                self._test_settings['port_manager_min_port'])
        self.assertLessEqual(port,
                             self._test_settings['port_manager_max_port'])

    def test_no_range_port(self):
        """ This test checks that it is possible to get a port
        from self._port_manager without specifying min and max ports
        """

        with patch.dict(self._test_settings,
                        {'port_manager_min_port': None,
                         'port_manager_max_port': None}):
            self._port_manager.configure(self._test_settings)
            port = self._port_manager.get_port()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("127.0.0.1", port))
            s.close()
            self.assertIsNotNone(port)

    def test_port_not_avail(self):
        """ This test checks that, when the port scan fails twice,
        an exception is raised.
        """
        with patch(self._port_manager.__module__ + ".AvailablePort._scan_port")\
                as scan_port_patch:
            scan_port_patch.return_value = None
            with self.assertRaises(PortNotAvailable):
                self._port_manager.get_port()

    def test_scan_port_invalid_ip_address(self):
        """ This test verifies functionality when ip_address is invalid.
        """
        with patch(self._port_manager.__module__ + ".raw_socket")\
                as raw_socket_patch:
            with patch(self._port_manager.__module__ + ".Host") \
                    as host_patch:
                # cause binding to fail
                bind_mock = Mock()
                bind_mock.bind = Mock(side_effect=IOError)
                raw_socket_patch.return_value = bind_mock
                # since binding fails make it so the ip address is invalid
                # patch host to be invalid
                host_patch.is_valid = Mock(return_value=False)
                # patch host so that it fails to verify ip address
                host_patch.wait_for_ip_address = Mock(return_value=False)

                with self.assertRaises(InvalidIPAddress):
                    self._port_manager.get_port()

    def test_first_port_invalid(self):
        """ Allow port to be reassign after an initial failure
        """
        self._call_no = 1
        with patch(self._port_manager.__module__ + ".raw_socket")\
                as raw_socket_patch:
            with patch(self._port_manager.__module__ + ".Host") \
                    as host_patch:
                # cause binding to fail
                bind_mock = Mock()
                bind_mock.bind = self._bind_on_second_call
                raw_socket_patch.return_value = bind_mock
                # since binding fails make it so the ip address is valid
                # meaning port is to be blamed
                host_patch.is_valid = Mock(return_value=True)

                port = self._port_manager.get_port()
                # assert port is in range
                self.assertGreaterEqual(port, 7000)
                self.assertLessEqual(port, 7999)
                # assert different port was retried
                self.assertNotEqual(self._port, port)

    def test_ip_address_recover(self):
        """ Allow port to be retried after ip_address becomes available
        """
        self._call_no = 1
        with patch(self._port_manager.__module__ + ".raw_socket")\
                as raw_socket_patch:
            with patch(self._port_manager.__module__ + ".Host") \
                    as host_patch:
                # cause binding to fail
                bind_mock = Mock()
                bind_mock.bind = self._bind_on_second_call
                raw_socket_patch.return_value = bind_mock
                # since binding fails make it so the ip address is invalid
                host_patch.is_valid = Mock(return_value=False)
                # patch host so that ip address becomes available
                host_patch.wait_for_ip_address = Mock(return_value=True)

                port = self._port_manager.get_port()
                # assert port is in range
                self.assertGreaterEqual(port, 7000)
                self.assertLessEqual(port, 7999)
                # assert same port was retried
                self.assertEqual(self._port, port)

    def _bind_on_second_call(self, ip_and_port):
        if self._call_no == 1:
            self._call_no += 1
            (_, self._port) = ip_and_port
            raise IOError
        # allow second bind call to success
