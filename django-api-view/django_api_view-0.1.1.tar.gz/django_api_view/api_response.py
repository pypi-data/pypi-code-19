# -*- coding: utf-8
# Django
import json
from django.http import HttpResponse
from django.utils import six


class ApiResponse:

    def __init__(self, status=200, headers=None,
                 content_type='application/json'):
        self.status = status
        self.headers = headers
        self.content_type = content_type

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def get_headers(self):
        return self.headers

    def set_headers(self, headers):
        self.headers = headers

    def get_content_type(self):
        return self.content_type

    def set_content_type(self, content_type):
        self.content_type = content_type

    def get_error_data(self, data, message):
        return {
            'errors': {
                'message': message,
                'code': self.get_status(),
                'data': data,
            }
        }

    def api_response(self, data):
        response = HttpResponse(
            json.dumps(data),
            content_type=self.content_type,
            status=self.status)

        if self.headers:
            for name, value in six.iteritems(self.headers):
                response[name] = value

        return response

    def success(self, data=None):
        self.set_status(200)

        return self.api_response(data)

    def bad_request(self, data=None, message='Bad Request'):
        self.set_status(400)
        response_data = self.get_error_data(data, message)

        return self.api_response(response_data)

    def unauthorized(self, data=None, message='Unauthorized'):
        self.set_status(401)
        response_data = self.get_error_data(data, message)

        return self.api_response(response_data)

    def forbidden(self, data=None, message='Forbidden'):
        self.set_status(403)
        response_data = self.get_error_data(data, message)

        return self.api_response(response_data)

    def not_found(self, data=None, message='Not Found'):
        self.set_status(404)
        response_data = self.get_error_data(data, message)

        return self.api_response(response_data)

    def unprocessable_entity(self, data=None, message='Unprocessable Entity'):
        self.set_status(422)
        response_data = self.get_error_data(data, message)

        return self.api_response(response_data)

    def internal_server_error(
            self, data=None, message='Internal Server Error'):
        self.set_status(500)
        response_data = self.get_error_data(data, message)

        return self.api_response(response_data)

    def bad_gateway(self, data=None, message='Bad Gateway'):
        self.set_status(502)
        response_data = self.get_error_data(data, message)

        return self.api_response(response_data)

    def service_unavailable(self, data=None, message='Service Unavailable'):
        self.set_status(503)
        response_data = self.get_error_data(data, message)

        return self.api_response(response_data)

    def gateway_timeout(self, data=None, message='Gateway timeout'):
        self.set_status(504)
        response_data = self.get_error_data(data, message)

        return self.api_response(response_data)
