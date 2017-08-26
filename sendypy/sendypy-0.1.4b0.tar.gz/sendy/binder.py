from __future__ import unicode_literals

import json
import logging
import requests
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin
from .exceptions import SendyError


log = logging.getLogger(__name__)


def convert_to_utf8(value):
    try:
        unicode
    except NameError:
        return value
    if isinstance(value, str):
        value = unicode(value)
    if isinstance(value, unicode):
        return value.decode('utf-8')
    return value


def bind_api(**config):

    class APIMethod(object):
        path = config['path']
        allowed_param = config.get('allowed_param', [])
        method = config.get('method', 'GET')
        require_auth = config.get('require_auth', True)
        success_status_code = config.get('success_status_code', 200)
        success_message = config.get('success_message', None)
        extra_param = config.get('extra_param', None)
        fail_silently = config.get('fail_silently', True)

        def __init__(self, api, args, kwargs):
            self.api = api
            self.headers = kwargs.pop('headers', {})
            self.post_data = kwargs.pop('post_data', None)
            self.build_parameters(args, kwargs)
            self.path = self.path.format(**self.parameters)  # Sub any URL vars
            self.host = api.host

            if not isinstance(self.success_message, (list, tuple)):
                self.success_message = [self.success_message]

        def build_parameters(self, args, kwargs):
            self.parameters = {}
            for idx, arg in enumerate(args):
                if arg is None:
                    continue

                try:
                    self.parameters[self.allowed_param[idx]] = \
                                                    convert_to_utf8(arg)
                except IndexError:
                    raise ValueError('Too many parameters supplied!')

            for k, arg in kwargs.items():
                if arg is None:
                    continue
                if k in self.parameters:
                    raise ValueError(
                        'Multiple values for parameter {0} supplied!'.format(k)
                    )

                self.parameters[k] = convert_to_utf8(arg)

            if self.extra_param is not None:
                self.parameters.update(self.extra_param)

            if self.require_auth and self.api.api_key is not None:
                self.parameters['api_key'] = self.api.api_key

        def execute(self):
            # Build the request URL
            url = urljoin(self.host, self.path)

            if self.api.debug:
                log.info('* Sending {0}: {1}\nHeaders: {2}\nData:{3}'.format(
                    self.method,
                    url,
                    self.headers,
                    self.post_data,
                ))

            response = requests.request(
                self.method,
                url,
                headers=self.headers,
                data=self.parameters,
            )
            data = response.content
            if callable(self.success_message):
                try:
                    return self.success_message(data)
                except ValueError:
                    if not self.fail_silently:
                        raise SendyError(data)

            success = data in self.success_message
            if not success and not self.fail_silently:
                raise SendyError(data)
            return data


    def _call(api, *args, **kwargs):
        method = APIMethod(api, args, kwargs)
        return method.execute()

    return _call
