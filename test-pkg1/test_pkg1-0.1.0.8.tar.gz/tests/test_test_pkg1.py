#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `test_pkg1` package."""


import unittest
from click.testing import CliRunner

from test_pkg1 import test_pkg1
from test_pkg1 import cli


class TestTest_pkg1(unittest.TestCase):
    """Tests for `test_pkg1` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.hello_message = "Hello, World!"

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_prints_hello(self):
        output = cli.hello()
        assert(output == self.hello_message)

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'test_pkg1.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
