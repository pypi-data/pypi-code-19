import unittest

import testdocker
from testdocker import (
    ContainerTestMixinBase,
    ContainerTestMixin,
    CommandBase,
    CurlCommand,
    NetCatCommand,
    CatCommand,
    Container
)


class TestContainer(ContainerTestMixin, unittest.TestCase):
    """Run basic tests on <project> container.

    Attributes:
        name:
            (str) Name for container.
        tear_down:
            (bool) Should ``docker-compose down`` be run in ``tearDownClass?``.
        compose_files:
            (list) List of docker-compose files to load for testing.
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
    tear_down = False
    test_patterns = [
        r"",
        r"",
        r"",
        r"",
        r"",
    ]
    test_tcp_ports = []
    test_upd_ports = []
    test_http_uris = [
        'http://',
        'http://',
        'http://',
    ]

    # sleep_interval = 8

    # @classmethod
    # def container_ready(self):
    #     return True

    def test_correct_<>_in_<>(self):
        """Assert correct  in """
        cmd = ''
        exit_code, output = self.container.exec(cmd)
        self.assertEqual(exit_code, 0)
        self.assertRegex(output, r'')

    def test_correct_<>_in_<>_json_matches_<>_in_env(self):
        """Assert correct  in  json matches  in environment"""
        cmd = 'cat <>.ini'
        exit_code, output = self.container.exec(cmd)
        self.assertEqual(exit_code, 0)

        data = json.loads(output)
        self.assertEqual(
            data.get(''),
            self.container.env['<PROJECT>_VAR']
        )

    def test_correct_<>_in_<>_ini_matches_<>_in_env(self):
        """Assert correct  in  matches  in environment"""
        cmd = 'cat <>.ini'
        exit_code, output = self.container.exec(cmd)
        self.assertEqual(exit_code, 0)

        parser = configparser.ConfigParser(strict=False)
        parser.read_string(output)
        self.assertEqual(
            parser.get('<section>', '<>'),
            self.container.env['<PROJECT>_VAR']
        )


class TestContainerExtended(ContainerTestMixinBase, unittest.TestCase):
    """Run extended tests on <project> container."""

    name = 'kazoo'
    tear_down = False


    def test_<>(self):
        """Assert <> was successful."""
        cmd = SomeCommand('arg1', 'arg2')
        exit_code, output = self.container.exec(cmd)
        output = output.split('\n')
        self.assertEqual(exit_code, 0)
        self.assertGreater(len(output), 1)
        self.assertRegex(output[-2], r'^')

    def test_<>(self):
        """Assert <> was successful."""
        cmd = SomeCommand('arg1', 'arg2')
        exit_code, output = self.container.exec(cmd)
        output = output.split('\n')
        self.assertEqual(exit_code, 0)
        self.assertGreater(len(output), 1)
        self.assertRegex(output[-2], r'^')

    def test_<>(self):
        """Assert <> was successful."""
        cmd = SomeCommand('arg1', 'arg2')
        exit_code, output = self.container.exec(cmd)
        output = output.split('\n')
        self.assertEqual(exit_code, 0)
        self.assertGreater(len(output), 1)
        self.assertRegex(output[-2], r'^')


if __name__ == '__main__':
    testdocker.main()
