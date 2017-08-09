import unittest
import sys
import os


sys.path.append("/Users/glucio/PycharmProjects/lambda-toolkit")

from lambda_toolkit.modules.conf import Conf


class TestConf(unittest.TestCase):
    def setUp(self):
        self.conf = Conf()

    def test_config_file_defined(self):
        self.assertTrue(self.conf.config_file is not None)

    def test_config_file_exists(self):
        self.assertTrue(os.path.isfile(self.conf.config_file))



if __name__ == '__main__':
    unittest.main()
