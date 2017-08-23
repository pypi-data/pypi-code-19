#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import sys
import json
import os

try:
    # Python 3.x
    from urllib.parse import urlencode
    import urllib.request as urlrequest
except ImportError:
    # Python 2.x
    from urllib import urlencode
    import urllib2 as urlrequest


class APIError(Exception):
    pass


def incoming_webhooks_api_request(url, payload):
    """Make request to Slack's incoming webhooks api."""

    payload = json.dumps(payload)
    data = urlencode({'payload': payload}).encode('utf-8')

    handler = urlrequest.HTTPHandler()
    opener = urlrequest.build_opener(handler)

    request = urlrequest.Request(url)
    response = opener.open(request, data)

    if response.getcode() != 200:
        raise APIError(response.msg)
    return True


def main():
    webhook_url = os.environ.get('SLACKCAT_WEBHOOK_URL')
    username = os.environ.get('SLACKCAT_USERNAME', 'slackcat')
    icon_url = os.environ.get('SLACKCAT_ICON_URL')

    parser = argparse.ArgumentParser(
        description='Pipe command output to Slack from your terminal!',
    )
    parser.add_argument('channel', help='output "@channel" or @user')
    parser.add_argument('file', help='target file to cat', nargs='?',
                        default=None)
    arguments = parser.parse_args()

    if not sys.stdin.isatty():
        text = sys.stdin.read()
    elif arguments.file:
        with open(arguments.file) as fh:
            text = fh.read()
    else:
        parser.print_help()
        exit(1)

    incoming_webhooks_api_request(webhook_url, {
        'username': username,
        'icon_url': icon_url,
        'channel': arguments.channel,
        'text': '```' + text + '```',
    })


if __name__ == '__main__':
    main()
