# coding: utf-8
#
# Copyright (c) 2017 Boris Tatarintsev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

"""Collection of short functions to simplify tornado-based clients testing.

Provides tools to simplify http server emulation for thorough tests of
tornado-based clients in a closest to real world way.

See tests/test_async_decorator.py for examples.
"""

import time

from tornado import gen
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

type_name_builder = '{prefix}_{name}'.format
func_type = type(lambda: 0)


class _GetResponse(RequestHandler):
    def initialize(self, response, extra):
        self.__response = response

        self.__delay_sec = extra.get('response_delay_sec', 0)
        self.__write_error = extra.get('write_error', None)

    @gen.coroutine
    def get(self):

        time.sleep(self.__delay_sec)

        if self.__write_error is None:
            self.write(self.__response)
            self.finish()
        else:
            self.write_error(self.__write_error)


def get_hdlr_helper(hdlr_func):
    """
    Convenience function that helps create user defined get-handlers
    with easecall

    :param hdlr_func: handler function
    :return: constructed class with a handler from user function
    """

    writer = lambda self, *args, **kwargs: self.finish(self.write(hdlr_func(*args, **kwargs)))
    new_klass = type(type_name_builder(prefix=id(hdlr_func), name='TestGet'),
                     (RequestHandler,), {})
    setattr(new_klass, 'get', writer)

    return new_klass


def __setup(klass, user_setup_method):
    def nested(inst):
        super(klass, inst).setUp()
        user_setup_method(inst)

    return nested


def __teardown(klass, user_setup_method):
    def nested(inst):
        super(klass, inst).tearDown()
        user_setup_method(inst)

    return nested


def __insert_methods(src_klass, dst_klass):
    for name, body in src_klass.__dict__.items():

        if name == 'setUp':
            setattr(dst_klass, 'setUp', __setup(dst_klass, body))

        elif name == 'tearDown':
            setattr(dst_klass, 'tearDown', __teardown(dst_klass, body))

        elif name.startswith('test_') and isinstance(body, func_type):
            setattr(dst_klass, name, body)


def async_server(hdlrs_responses):
    """
    Simple decorator to make testing Tornado async apps easier.

    Starts local server with handlers and responses
    given in arguments.

    Extra options are allowed.

    :param list[(str, str, dict[str, Any])|(str, function)] hdlrs_responses: list of
    (handler, response, params) triplets or (handler, function) pairs
    """

    def new_type_gen(klass):

        server_handlers = []

        for triplet in hdlrs_responses:
            handler, rest = triplet[0], triplet[1]
            if isinstance(rest, str):
                response, extra = triplet[1:]
                server_handlers.append((handler, _GetResponse, {'response': response,
                                                                'extra': extra}))
            else:
                hdlr_func = rest
                server_handlers.append((handler, hdlr_func))

        new_type_name = type_name_builder(prefix=klass.__name__, name='Test')

        new_klass = type(new_type_name, (AsyncHTTPTestCase,),
                         {'get_app': lambda self: Application(server_handlers)})

        __insert_methods(klass, new_klass)

        return new_klass

    return new_type_gen
