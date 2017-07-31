import werkzeug
import json


class Response:

    def __init__(self, *args, **kwargs):
        self.res = werkzeug.wrappers.Response(*args, **kwargs)

    def get_status(self):
        return self.res.status_code

    def status(self, status):
        self.res.status_code = status
        return self

    def get_content_type(self):
        return self.res.content_type

    def content_type(self, content_type):
        self.res.content_type = content_type
        return self

    def get_body(self):
        return self.res.get_data(True)

    def body(self, body):
        self.res.set_data(body)
        return self

    def html(self, html):
        return self.content_type('text/html').body(html)

    def json(self, obj):
        return self.content_type('application/json').body(json.dumps(obj))

    def text(self, text):
        return self.content_type('text/plain').body(text)
