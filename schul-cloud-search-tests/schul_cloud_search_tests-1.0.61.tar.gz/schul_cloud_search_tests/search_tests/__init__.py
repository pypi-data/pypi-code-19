"""
These tests are run by the proxy.
They test whether requests of the client and responses of the server are correct.

The tests in schul_cloud_search_tests.tests test that these tests work.

"""
import pytest
import os
import threading
import io
import traceback
import inspect
from bottle import request

HERE = os.path.dirname(__file__)
_local = threading.local()
SOURCE_BASE = "https://github.com/schul-cloud/schul_cloud_search_tests/tree/master/schul_cloud_search_tests"


def get_test_function(tb):
    """Return the documentation from the first test functions found."""
    while tb:
        for func in tb.tb_frame.f_globals.values():
            if inspect.isfunction(func) and \
                    func.__name__.startswith("test_") and \
                    func.__code__ == tb.tb_frame.f_code:
                return func
        tb = tb.tb_next


def run_request_tests(request_url):
    """Run the tests with the request."""
    return _run_tests_and_collect_errors(request_url, ["-m" "request", HERE])


def run_response_tests(request_url, response):
    """Run the tests with the request and response."""
    _local.response = response
    try:
        return _run_tests_and_collect_errors(request_url, ["-m" "not request", HERE])
    finally:
        del _local.response


def get_response():
    """Return the currently working response."""
    return _local.response


def get_request_url():
    """Return the url of the test server endpoint with the query."""
    return _local.request_url


def get_source_url(function, base=None):
    """Return the source url of the function where the source code resides."""
    if base is None:
        host = request.headers.get("host", None)
        if host is None:
            url = SOURCE_BASE
        else:
            url = "http://" + host + "/code"
    else:
        url = base
    base = os.path.abspath(os.path.dirname(HERE))
    path = os.path.abspath(function.__globals__.get("__file__", ""))
    if not path.startswith(base):
        return None
    return url + path[len(base):].replace("\\", "/") + "#L" + str(function.__code__.co_firstlineno)


def add_failing_test(ty, err, tb):
    """Add a failing test to the tests of this request."""
    file = io.StringIO()
    traceback.print_exception(ty, err, tb, file=file)
    tb_string = file.getvalue()
    test = get_test_function(tb)
    _local.failing_tests.append({
          "status": 500, 
          "title": "Internal Server Error",
          "detail": ty.__name__ + ": " + str(err),
          "meta": {
            "traceback" : tb_string,
            "documentation": (test.__doc__ if test else None),
            "test_function": (test.__name__ if test else None),
            "source": (get_source_url(test) if test else None),
            "source-line": (test.__code__.co_firstlineno if test else None),
            "error-class": ty.__module__ + "." + ty.__name__,
            "error": str(err),
            "github-url": (get_source_url(test, SOURCE_BASE) if test else None),
          }
        })


def _run_tests_and_collect_errors(request_url, args):
    """Run the tests and collect the errors in these tests."""
    _local.failing_tests = []
    _local.request_url = request_url
    try:
        pytest.main(args)
        return _local.failing_tests
    finally:
        del _local.failing_tests
        del _local.request_url

