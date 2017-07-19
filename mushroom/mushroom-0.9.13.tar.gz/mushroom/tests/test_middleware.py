import unittest

from mushroom.rpc.middleware import Middleware, MiddlewareStack
from mushroom.rpc.exceptions import RpcError
from mushroom.rpc.exceptions import RequestException
from mushroom.rpc.dispatcher import MethodDispatcher


class MockRequest(object):

    def __init__(self, method, data=None):
        self.method = method
        self.data = data


class MyError(RuntimeError):
    pass


class ErrorMiddleware(Middleware):

    def __call__(self, request):
        try:
            return super(ErrorMiddleware, self).__call__(request)
        except MyError as e:
            raise RequestException(e.message)


count = 0;


class CountMiddleware(Middleware):

    def __call__(self, request):
        global count
        count += 1
        try:
            return super(CountMiddleware, self).__call__(request)
        finally:
            count -= 1


class RpcMethods(object):

    def rpc_fail(self, request):
        raise MyError('Fail!')

    def rpc_count(self, request):
        return count


class MiddlewareTestCase(unittest.TestCase):

    def setUp(self):
        self.rpc_handler = MiddlewareStack([
            ErrorMiddleware,
            CountMiddleware
        ], MethodDispatcher(RpcMethods()))

    def test_error(self):
        self.assertRaises(
                RequestException,
                self.rpc_handler,
                MockRequest('fail'))
        self.assertEquals(count, 0)

    def test_count(self):
        self.assertEquals(self.rpc_handler(MockRequest('count', None)), 1)
        self.assertEquals(count, 0)
