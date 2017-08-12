import json

import requests


_default_api_obj = None

def setup(project_id, api_key):
    global _default_api_obj
    _default_api_obj = MessageApi(
        project_id,
        api_key
    )

def _default_api():
    if _default_api_obj is None:
        raise ValueError(
            "Must call setup() on channel module first, "
            "or create a channel.MessageAPI instance"
        )
    return _default_api_obj

def create_channel(*args, **kwargs):
    _default_api().create_channel(*args, **kwargs)

def send_message(*args, **kwargs):
    _default_api().send_message(*args, **kwargs)

class MessageApi(object):
    def __init__(self, project_id=None, api_key=None):
        self.project_id = project_id
        self.api_key = api_key

    def create_channel(self, client_id, duration_minutes=None):
        params = {
            "project_id": self.project_id
        }
        body = {
            "channel_id": client_id
        }
        response = self._send_request("post", params=params, json=body)
        return response["token"]


    def send_message(self, client_id, message):
        params = {
            "project_id": self.project_id
        }
        body = {
            "channel_id": client_id,
            "message": message
        }
        response = self._send_request("post", params=params, json=body)
        return None

    def _send_request(self, method, *args, **kwargs):
        request_func = getattr(requests, method)
        kwargs.setdefault("headers", {})
        kwargs["headers"].setdefault("X-API-Key", self.api_key)
        response = request_func(*args, **kwargs)
        response.raise_for_status()
        response_body = None
        if response.status_code == 200 and response.text:
            response_body = json.loads(response.text)
        return response_body

