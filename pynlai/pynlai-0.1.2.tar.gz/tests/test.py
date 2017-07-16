#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
test
----

unit tests for pynlai package
'''


import unittest
from click.testing import CliRunner

from pynlai import core
from pynlai import cli


class Test(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass

    def test_cli(self):
        result = self.runner.invoke(
            cli.main,
            catch_exceptions=False,
        )
        self.assertEqual(result.exit_code, 0)

    def test_cli_help(self):
        result = self.runner.invoke(
            cli.main,
            ['--help'],
            catch_exceptions=False,
        )
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Show this message and exit' in result.output)

    def test_cli_parse(self):
        pass
