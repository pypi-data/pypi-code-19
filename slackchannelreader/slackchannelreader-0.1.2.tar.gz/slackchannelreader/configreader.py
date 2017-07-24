"""
Reads the Slack authentication data from environment variables or config files.
"""

import os
import re


class Config:
    """
    Read the Slack authentication data.
    """
    def __init__(self):
        """
        Init with Slack authentication data form environment variables.
        """
        if 'SLACK_TOKEN' in os.environ:
            self.token = os.environ['SLACK_TOKEN']
        else:
            self.token = None

        if 'SLACK_CHANNEL' in os.environ:
            self.channel = os.environ['SLACK_CHANNEL']
        else:
            self.channel = None

    def read(self, file):
        for k, v in read_file(file):
            if k == 'token':
                self.token = v
            elif k == 'channel':
                self.channel = v


def read_file(file):
    if not os.path.isfile(file):
        raise IOError('File %s does not exist!' % file)

    with open(file, encoding='utf-8', mode='r') as f:
        expr = re.compile(r"(?P<key>[a-zA-Z ]+)=(?P<value>.*)")

        while True:
            line = f.readline()

            if not line:
                break

            line = line.strip()

            m = expr.match(line)
            if m:
                key = m.group('key')
                value = m.group('value')
                yield (key.strip().lower(), value.strip())
