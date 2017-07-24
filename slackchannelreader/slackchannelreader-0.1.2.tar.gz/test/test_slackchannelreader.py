"""
Test for slackchannelreader.slackchannelreader.
"""
import os
import unittest
from time import sleep

from slackchannelreader.slackchannelreader import SlackInfoClient


class ICalDownloadTests(unittest.TestCase):

    def test_request(self):
        conf = None
        conf_file = "slack.txt"
        if os.path.isfile(conf_file):
            conf = conf_file
        client = SlackInfoClient(config_file=conf)
        client.request()

        sleep(15)

        self.assertFalse(client.is_updating())

        msg_limit = 3
        img_limit = 1

        msgs = client.messages(limit=msg_limit)
        imgs = client.images(limit=img_limit)

        print("%d messages" % len(msgs))

        print("%d images" % len(imgs))
        for img in imgs:
            print("%s exist? %s" % (img, os.path.isfile(img)))

        self.assertTrue(len(msgs) <= msg_limit, "message count")
        self.assertTrue(len(imgs) <= img_limit, "image count")
