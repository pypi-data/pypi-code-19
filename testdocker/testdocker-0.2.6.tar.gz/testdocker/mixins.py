"""
testdocker.mixins
~~~~~~~~~~~~~~~~~

Unit Test mixins for testing docker containers.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import time
import unittest

from colour_runner.runner import ColourTextTestRunner
from colour_runner.result import ColourTextTestResult

from . import util, objects, commands


class ContainerTestMixinBase:
    """For testing <project> container.

    Attributes:
        name:
            (str) Name for container.
        compose_files:
            (list) List of docker-compose files to load for testing.
        tear_down:
            (bool) Should ``docker-compose down`` be run in ``tearDownClass?``.
    """

    name = ''
    compose_files = []
    tear_down = True

    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, 'name'):
            raise RuntimeError('Test class missing name attribute')
        compose_files = getattr(cls, 'compose_files')
        cls.compose = objects.Compose(options=dict(files=compose_files))
        cls.containers = cls.compose.up()
        if not all(c.health == 'healthy' for c in cls.containers):
            print('Waiting for: %s to be ready...' % cls.containers)
            for container in cls.containers:
                container.wait()
        cls.container = util.select_one(
            cls.containers, where='name', equals=cls.name)

        if hasattr(cls, 'container_ready'):
            sleep_interval = getattr(cls, 'sleep_interval', 8)
            print('Waiting on container_ready hook to return True')
            while not cls.container_ready():
                time.sleep(sleep_interval)
        super(ContainerTestMixinBase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(ContainerTestMixinBase, cls).tearDownClass()
        if cls.tear_down:
            cls.compose.down()
        del cls.containers
        del cls.container
        del cls.compose

    def defaultTestResult(self):
        return ColourTextTestResult(
            descriptions=True,
            verbosity=2
        )


class ContainerTestMixin(ContainerTestMixinBase):
    """For testing <project> container.

    Attributes:
        name:
            (str) Name for container.
        compose_files:
            (list) List of docker-compose files to load for testing.
        tear_down:
            (bool) Should ``docker-compose down`` be run in ``tearDownClass?``.
        test_patterns:
            (list) Regex patterns to assert in  container logs.
        test_tcp_ports:
            (list) TCP Ports to assert are open
        test_upd_ports:
            (list) TCP Ports to assert are open
        test_http_uris:
            (list) HTTP URI's to test are reachable
    """

    name = ''
    compose_files = []
    tear_down = True
    test_patterns = []
    test_tcp_ports = []
    test_udp_ports = []
    test_http_uris = []

    def test_container_is_healthy(self):
        """Assert container healthcheck is passing"""
        self.assertEqual(self.container.health, 'healthy')

    def test_patterns_in_logs(self):
        """Assert test_patterns appear in container logs"""
        logs = self.container.logs
        for pattern in self.test_patterns:
            with self.subTest(pattern=pattern):
                self.assertRegex(logs, pattern)

    def test_tcp_ports_open(self):
        """Assert test_tcp_ports are open"""
        for port in self.test_tcp_ports:
            with self.subTest(port=port):
                cmd = commands.NetCatCommand('localhost', port)
                exit_code = self.container.exec(cmd, exit_code_only=True)
                self.assertEqual(exit_code, 0)

    def test_udp_ports_open(self):
        """Assert test_udp_ports are open"""
        for port in self.test_udp_ports:
            with self.subTest(port=port):
                cmd = commands.NetCatCommand('localhost', port, udp=True)
                exit_code = self.container.exec(cmd, exit_code_only=True)
                self.assertEqual(exit_code, 0)

    def test_http_uris_reachable(self):
        """Assert test_http_uris are reachable"""
        for uri in self.test_http_uris:
            with self.subTest(uri=uri):
                cmd = commands.CurlCommand(uri)
                exit_code = self.container.exec(cmd, exit_code_only=True)
                self.assertEqual(exit_code, 0)


def main():
    """Execute the tests"""
    unittest.main(
        testRunner=ColourTextTestRunner(verbosity=2, descriptions=True),
        verbosity=2,
    )
