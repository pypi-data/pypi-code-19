import json
import logging

import requests
from base64 import urlsafe_b64encode
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .exceptions import FaaspotException

DEFAULT_PORT = 80
SECURED_PORT = 443
SECURED_PROTOCOL = 'https'
DEFAULT_PROTOCOL = 'http'
DEFAULT_API_VERSION = ''
BASIC_AUTH_PREFIX = 'Basic'
AUTHENTICATION_HEADER = 'Authorization'
TOKEN_AUTHENTICATION_HEADER = 'Token'

# The __name__ is fas.client.httpclient
# So, to separate log level "fas.*" modules and this module,
# I changes the logger name, to be "fas_client.*", and not "fas.*"
logger = logging.getLogger('fas_client.httpclient')
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class HTTPClient(object):

    def __init__(self, host, port=DEFAULT_PORT,
                 protocol=DEFAULT_PROTOCOL, api_version=DEFAULT_API_VERSION,
                 headers=None, query_params=None, cert=None, trust_all=False,
                 username=None, password=None, token=None):
        self.port = port
        self.host = host
        self.protocol = protocol
        self.api_version = api_version
        self.headers = headers.copy() if headers else {}
        if not self.headers.get('Content-type'):
            self.headers['Content-type'] = 'application/json'
        self.query_params = query_params.copy() if query_params else {}
        self.logger = logger
        self.cert = cert
        self.trust_all = trust_all
        self._set_header(AUTHENTICATION_HEADER, self._get_auth_header(username, password),
                         log_value=False)
        self._set_header(AUTHENTICATION_HEADER, self._get_token_header(token),
                         log_value=True)

    @property
    def url(self):
        url = '{0}://{1}:{2}/v1/{3}'.format(self.protocol, self.host,
                                            self.port, self.api_version)
        self.logger.debug('Using url: {0}'.format(url))
        return url

    def verify_response_status(self, response, expected_code=200):
        if response.status_code != expected_code:
            self._raise_client_error(response)

    def get_request_verify(self):
        if self.cert:
            # verify will hold the path to the self-signed certificate
            return self.cert
        # certificate verification is required iff trust_all is False
        return not self.trust_all

    def do_request(self,
                   requests_method,
                   uri,
                   data=None,
                   params=None,
                   headers=None,
                   expected_status_code=200,
                   stream=False,
                   versioned_url=True,
                   timeout=None):
        if versioned_url:
            request_url = '{0}{1}'.format(self.url, uri)
        else:
            # remove version from url ending
            url = self.url.rsplit('/', 1)[0]
            request_url = '{0}{1}'.format(url, uri)

        # build headers
        headers = headers or {}
        total_headers = self.headers.copy()
        total_headers.update(headers)

        # build query params
        params = params or {}
        total_params = self.query_params.copy()
        total_params.update(params)

        # data is either dict, bytes data or None
        is_dict_data = isinstance(data, dict)
        body = json.dumps(data) if is_dict_data else data
        if self.logger.isEnabledFor(logging.DEBUG):
            log_message = 'Sending request: {0} {1}'.format(
                requests_method.func_name.upper(),
                request_url)
            if is_dict_data:
                log_message += '; body: {0}'.format(body)
            elif data is not None:
                log_message += '; body: bytes data'
            self.logger.debug(log_message)
        return self._do_request(
            requests_method=requests_method, request_url=request_url,
            body=body, params=total_params, headers=total_headers,
            expected_status_code=expected_status_code, stream=stream,
            verify=self.get_request_verify(), timeout=timeout)

    def get(self, uri, data=None, params=None, headers=None, _include=None,
            expected_status_code=200, stream=False, versioned_url=True,
            timeout=None):
        if _include:
            fields = ','.join(_include)
            if not params:
                params = {}
            params['_include'] = fields
        return self.do_request(requests.get,
                               uri,
                               data=data,
                               params=params,
                               headers=headers,
                               expected_status_code=expected_status_code,
                               stream=stream,
                               versioned_url=versioned_url,
                               timeout=timeout)

    def put(self, uri, data=None, params=None, headers=None,
            expected_status_code=200, stream=False, timeout=None):
        return self.do_request(requests.put,
                               uri,
                               data=data,
                               params=params,
                               headers=headers,
                               expected_status_code=expected_status_code,
                               stream=stream,
                               timeout=timeout)

    def patch(self, uri, data=None, params=None, headers=None,
              expected_status_code=200, stream=False, timeout=None):
        return self.do_request(requests.patch,
                               uri,
                               data=data,
                               params=params,
                               headers=headers,
                               expected_status_code=expected_status_code,
                               stream=stream,
                               timeout=timeout)

    def post(self, uri, data=None, params=None, headers=None,
             expected_status_code=200, stream=False, timeout=None):
        return self.do_request(requests.post,
                               uri,
                               data=data,
                               params=params,
                               headers=headers,
                               expected_status_code=expected_status_code,
                               stream=stream,
                               timeout=timeout)

    def delete(self, uri, data=None, params=None, headers=None,
               expected_status_code=200, stream=False, timeout=None):
        return self.do_request(requests.delete,
                               uri,
                               data=data,
                               params=params,
                               headers=headers,
                               expected_status_code=expected_status_code,
                               stream=stream,
                               timeout=timeout)

    def _raise_client_error(self, response, url=None):
        try:
            result = response.json()
        except Exception:
            # Handle un-handled server errors (`regular` Exceptions on server)
            server_traceback = None
            error_code = None
            message = response.content
            if url:
                message = '{0} [{1}]'.format(message, url)
        else:
            if isinstance(result, dict):
                server_traceback = result.get('server_traceback')
                error_code = result.get('error_code')
                message = result['message'] if 'message' in result else None
                if not message:
                    message = result['detail'] if 'detail' in result else None
            else:
                message = result
                error_code = None
                server_traceback = None
        self._prepare_and_raise_exception(
            message=message,
            error_code=error_code,
            reason=response.reason,
            status_code=response.status_code,
            server_traceback=server_traceback)

    @staticmethod
    def _prepare_and_raise_exception(message,
                                     error_code,
                                     status_code,
                                     reason=None,
                                     server_traceback=None):
        raise FaaspotException(message,
                               reason,
                               server_traceback,
                               status_code,
                               error_code=error_code)

    def _do_request(self, requests_method, request_url, body, params, headers,
                    expected_status_code, stream, verify, timeout):
        response = requests_method(request_url,
                                   data=body,
                                   params=params,
                                   headers=headers,
                                   stream=stream,
                                   verify=verify,
                                   timeout=timeout,)
        log_headers = False
        if self.logger.isEnabledFor(logging.DEBUG):
            if log_headers:
                for hdr, hdr_content in response.request.headers.iteritems():
                    self.logger.debug('request header:  %s: %s' % (hdr, hdr_content))
            self.logger.debug('reply:  "%s %s" %s'
                              % (response.status_code,
                                 response.reason, response.content))
            if log_headers:
                for hdr, hdr_content in response.headers.iteritems():
                    self.logger.debug('response header:  %s: %s' % (hdr, hdr_content))

        if response.status_code != expected_status_code:
            self._raise_client_error(response, request_url)

        if stream:
            return StreamedResponse(response)

        return response.json()

    def _get_auth_header(self, username, password):
        if not username or not password:
            return None
        credentials = '{0}:{1}'.format(username, password)
        encoded_credentials = str(urlsafe_b64encode(str(credentials).encode('utf-8')))
        return BASIC_AUTH_PREFIX + ' ' + encoded_credentials

    def _get_token_header(self, token):
        if not token:
            return None
        return '{0} {1}'.format(TOKEN_AUTHENTICATION_HEADER, token)

    def _set_header(self, key, value, log_value=True):
        if not value:
            return
        self.headers[key] = value
        value = value if log_value else '*'
        self.logger.debug('Setting `{0}` header: {1}'.format(key, value))


class StreamedResponse(object):

    def __init__(self, response):
        self._response = response

    @property
    def headers(self):
        return self._response.headers

    def bytes_stream(self, chunk_size=8192):
        return self._response.iter_content(chunk_size)

    def lines_stream(self):
        return self._response.iter_lines()

    def close(self):
        self._response.close()
