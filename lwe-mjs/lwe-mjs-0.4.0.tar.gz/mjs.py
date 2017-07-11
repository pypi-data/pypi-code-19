# -*- coding: utf-8 -*-
from http import server, cookies
import socketserver
import json
import datetime
import traceback
import logging

import mapper

logger = logging.getLogger(__name__)

_validator = None
_validator_excludes = None
_incl_access_control_allow_origin = False
_incl_access_control_allow_credentials = False


class _RequestHandler(server.BaseHTTPRequestHandler):
    _mpr = mapper.Mapper.get()

    _status_code = None
    _message = None
    _cookie = None
    _payload = None

    def do_GET(self):
        if not self._validate():
            return

        try:
            resp = self._mpr.call(url=self.path, method='GET',
                                  args={'headers': self.headers})

        except Exception as e:
            traceback.print_exc()
            self._send_error(e)
            return

        if resp:
            self._handle_mapper_response(resp)

            self.send_response(self._status_code, self._message)
            self.send_header('Content-type', 'application/json')
            self._send_default_headers()
            self.end_headers()

            if self._payload is not None:
                self.wfile.write(bytes(json.dumps(
                    self._payload, default=self._serialize), 'utf-8'))

            else:
                self.wfile.write(bytes(json.dumps([]), 'utf-8'))

        else:
            self.send_response(400)
            self._send_default_headers()
            self.end_headers()

    def do_POST(self):
        if not self._validate():
            return

        content_length = int(self.headers['Content-Length'])

        try:
            data = self.rfile.read(content_length).decode('utf-8')
            if data:
                data = json.loads(data)
            else:
                data = {}

        except Exception as e:
            traceback.print_exc()
            self._send_error('Received invalid json')
            return

        try:
            resp = self._mpr.call(
                url=self.path, method='POST',
                args={'headers': self.headers, 'payload': data})

        except Exception as e:
            traceback.print_exc()
            self._send_error(e)
            return

        if resp:
            self._handle_mapper_response(resp)

            self.send_response(self._status_code, self._message)
            self.send_header('Content-type', 'application/json')
            self._send_default_headers()

            if self._cookie:
                self.send_header('Set-Cookie', self._cookie.output(header=''))

            self.end_headers()

        else:
            self.send_response(400)
            self._send_default_headers()
            self.end_headers()

    def do_PUT(self):
        if not self._validate():
            return

        content_length = int(self.headers['Content-Length'])

        try:
            data = json.loads(self.rfile.read(content_length).decode('utf-8'))

        except Exception as e:
            traceback.print_exc()
            self._send_error('Received invalid json')
            return

        try:
            resp = self._mpr.call(
                url=self.path, method='PUT',
                args={'headers': self.headers, 'payload': data})

        except Exception as e:
            traceback.print_exc()
            self._send_error(e)
            return

        if resp:
            self._handle_mapper_response(resp)
            self.send_response(self._status_code, self._message)

        else:
            self.send_response(400)

        self._send_default_headers()
        self.end_headers()

    def do_DELETE(self):
        if not self._validate():
            return

        try:
            resp = self._mpr.call(url=self.path, method='DELETE',
                                  args={'headers': self.headers})

        except Exception as e:
            traceback.print_exc()
            self._send_error(e)
            return

        if resp:
            self._handle_mapper_response(resp)
            self.send_response(self._status_code, self._message)

        else:
            self.send_response(400)

        self._send_default_headers()
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_default_headers()
        self.send_header('Access-Control-Allow-Methods',
                         'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _serialize(self, obj):
        if isinstance(obj, datetime.datetime):
            serial = obj.isoformat()

        return serial

    def _validate(self):
        if not _validator:
            return True

        if _validator_excludes:
            if self.path in _validator_excludes:
                return True

        try:
            valid = _validator(self.path, self.headers)

        except Exception as e:
            traceback.print_exc()
            self._send_error(e)
            return False

        if not valid:
            self.send_response(401)
            self._send_default_headers()
            self.end_headers()

            return False

        return True

    def _get_cookies(self):
        cookie = self.headers.get('Cookie')
        if not cookie:
            return None

        return cookies.BaseCookie(cookie)

    def _handle_mapper_response(self, response):
        self._status_code = response['status_code']
        self._message = response['message'] if 'message' in response else ''
        self._cookie = response['cookie'] if 'cookie' in response else None
        self._payload = response['payload'] if 'payload' in response else None

    def _send_error(self, error_message):
        self.send_response(500, error_message)
        self.send_header('Content-type', 'text/plain')
        self._send_default_headers()
        self.end_headers()

    def _send_default_headers(self):
        if _incl_access_control_allow_origin:
            if 'Origin' in self.headers:
                self.send_header('Access-Control-Allow-Origin',
                                 self.headers['Origin'])

            else:
                self.send_header('Access-Control-Allow-Origin', '*')

        self.send_header('Access-Control-Allow-Credentials',
                         str(_incl_access_control_allow_credentials).lower())

    def log_message(self, format, *args):
        logger.info(format % args)


class Config(object):
    """Config to be passed to the Server

    Attributes:
        address (str): The address to be used by the server.

        port (int): The port to be used by the server.

        incl_access_control_allow_origin (bool): Determines if
            'Access-Control-Allow-Origin' should be includedin the servers
            response header or not.

        incl_access_control_allow_credentials (bool): Determines if
            'Access-Control-Allow-Credentials' should be set to 'true' or
            'false' in the servers response header.

        validate_callback (function): A callback which will be called for
            EVERY request (GET, POST, PUT, DELETE) BEFORE the actual resolved
            function will be called.

            This callback HAS to return either True (if the request is
            allowed), or False (if the request is NOT allowed)

            Usefully to implement e.g. authentication

        validate_exclude_paths (list): A list of url-paths (without host:port)
            to be excluded from validation.

            e.g. ['/login', '/register']
    """

    address = '0.0.0.0'
    port = 8088
    incl_access_control_allow_origin = False
    incl_access_control_allow_credentials = False
    validate_callback = None
    validate_exclude_paths = None


class Server(server.HTTPServer):
    def __init__(self, conf):
        """Constructor to initialize the server

        Args:
            conf (Config): configuration for this server instance
        """
        if conf.validate_callback:
            global _validator
            _validator = conf.validate_callback

        if conf.validate_exclude_paths:
            global _validator_excludes
            _validator_excludes = conf.validate_exclude_paths

        if conf.incl_access_control_allow_origin:
            global _incl_access_control_allow_origin
            _incl_access_control_allow_origin = (
                conf.incl_access_control_allow_origin)

        if conf.incl_access_control_allow_credentials:
            global _incl_access_control_allow_credentials
            _incl_access_control_allow_credentials = (
                conf.incl_access_control_allow_credentials)

        super(Server, self).__init__((conf.address, conf.port),
                                     _RequestHandler)


class ThreadedServer(socketserver.ThreadingMixIn, Server):
    """Like `Server` but implements `socketserver.ThreadingMixIn` to
       handle request with multiple threads"""
    pass
