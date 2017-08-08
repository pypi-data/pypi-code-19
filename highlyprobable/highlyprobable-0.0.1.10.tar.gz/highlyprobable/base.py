import json
import logging
import os
import re
from datetime import datetime, timezone
from urllib.parse import urljoin
from uuid import uuid4

from pygments import highlight, lexers, formatters

logger = logging.getLogger(os.path.basename(__file__))

from highlyprobable.config import AI_API_ROOT_URL, META_API_ROOT_URL


class Base:
    def __init__(self, highlyprobable):
        self._hp = highlyprobable

    def _meta_url(self, url):
        return urljoin(META_API_ROOT_URL, url)

    def _ai_url(self, url):
        return urljoin(AI_API_ROOT_URL, url)

    def _format(self, data):
        return json.dumps(data, sort_keys=True, indent=4)


class APIBase:
    def __init__(self, highlyprobable, app):
        self._hp = highlyprobable
        self._app = app

    def _meta_url(self, url):
        return urljoin(META_API_ROOT_URL, url)

    def _ai_url(self, url):
        return urljoin(AI_API_ROOT_URL, url)

    def _format(self, data):
        return json.dumps(data, sort_keys=True, indent=4)


class Output:
    def __init__(self, data):
        self.data = data

    def print(self):
        formatted_json = json.dumps(self.data, sort_keys=True, indent=4)
        colourful_json = highlight(formatted_json.encode('utf-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
        print(colourful_json)

    def __repr__(self):
        return str(json.dumps(self.data, sort_keys=True, indent=4))


class Payload:
    def __init__(self, highlyprobable, app_name, payload):
        self.id = str(uuid4())
        self.highlyprobable = highlyprobable
        self.payload = payload
        self.app_name = app_name
        self.requested_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    def serialize(self):
        obj = {
            'request_id': self.id,
            'account': self.highlyprobable.manage.account.whoami.data,
            'app_name': self.app_name,
            'payload': self.payload,
            'requested_ms': self.requested_ms
        }
        obj['account']['auth_token'] = self.highlyprobable._secret_key
        return obj


def format_app_name(name):
    name = name.lower()
    name = re.sub('[^0-9a-zA-Z]+', '_', name)
    return name