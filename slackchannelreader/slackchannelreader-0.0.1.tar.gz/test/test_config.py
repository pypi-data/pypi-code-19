import os
import unittest

from slackchannelreader.configreader import Config


class ConifgTests(unittest.TestCase):

    def setUp(self):
        self.key_token = 'SLACK_TOKEN'
        self.key_channel = 'SLACK_CHANNEL'

    def test_config_from_environ(self):
        real_token = None
        real_channel = None

        if self.key_token in os.environ:
            real_token = os.environ[self.key_token]
        if self.key_channel in os.environ:
            real_channel = os.environ[self.key_channel]

        token = "123hallowelt"
        channel = "XYZ1235"

        os.environ[self.key_token] = token
        os.environ[self.key_channel] = channel

        config = Config()

        self.assertEqual(config.token, token, "token is env token")
        self.assertEqual(config.channel, channel, "channel is env channel")

        if real_token:
            os.environ[self.key_token] = real_token
        if real_channel:
            os.environ[self.key_channel] = real_channel

    def test_config_from_file(self):
        config = Config()
        config.read("test/test_data/config.txt")

        self.assertEqual(config.token, "asdfasdfHalloWelt123", "token from config file")
        self.assertEqual(config.channel, "XMASDF2345", "channel from config file")

    def test_config_from_file_error(self):
        with self.assertRaises(IOError):
            config = Config()
            config.read("test/test_data/does_not_exist.txt")

    def test_config_no_environ(self):
        real_token = None
        real_channel = None

        if self.key_token in os.environ:
            real_token = os.environ[self.key_token]
        if self.key_channel in os.environ:
            real_channel = os.environ[self.key_channel]

        del os.environ[self.key_token]
        del os.environ[self.key_channel]

        config = Config()

        self.assertEqual(config.token, None, "token is not set")
        self.assertEqual(config.channel, None, "channel is not set")

        if real_token:
            os.environ[self.key_token] = real_token
        if real_channel:
            os.environ[self.key_channel] = real_channel
