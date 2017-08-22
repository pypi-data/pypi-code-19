# encoding=utf8
import os
import unittest
from ghlint import config


class TestConfig(unittest.TestCase):

    def test_ghlintrc_path(self):
        ghlintrc_path = config.ghlintrc_path()
        expected_path = os.getcwd() + '/.ghlintrc'

        self.assertEqual(ghlintrc_path, expected_path)

    def test_settings_defaults(self):
        settings = config.settings()

        self.assertEqual(settings["account-type"], "user")
        self.assertEqual(settings["repo-type"], "owner")


if __name__ == '__main__':
    unittest.main()
