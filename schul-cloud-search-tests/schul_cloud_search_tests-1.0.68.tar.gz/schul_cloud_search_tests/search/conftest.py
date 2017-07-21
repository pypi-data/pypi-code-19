"""
This file contains the fixtures used in the tests in the same folder.

"""
from pytest import fixture
from urllib.parse import parse_qs, urlencode, urlparse
import requests
import sys
import os
from schul_cloud_resources_server_tests.tests.fixtures import (
    ParallelBottleServer)
import time
from pprint import pprint

HERE = os.path.dirname(__file__)
MODULE_ROOT = os.path.join(HERE, "..", "..")
try:
    import schul_cloud_search_tests
except ImportError:
    sys.path.append(MODULE_ROOT)
from schul_cloud_search_tests.proxy import get_app


DEFAULT_QUERIES = [{"Q":"einstein"}, {"Q":"test"}]


def pytest_addoption(parser):
    """Add options to pytest.

    This adds the options for
    - url to store the value
    - query to add the token to a list
    - max-depth to store the value
    """
    parser.addoption("--url", action="store",
        default="http://localhost:8080/v1/search",
        help="url: the url of the server api to connect to")
    parser.addoption("--max-depth", action="store", default=20,
        help="max-depth: This limits the number of requests"
             "which are executed to get all search results.")
    parser.addoption("--query", action="append", default=[],
        help="query: list of queries to ask the search engine")


def pytest_generate_tests(metafunc):
    """Generate parameters.

    - query
        These are some query parameters passed over via the command line
        
        If not enough parameters are specified, a set of own paramaters is taken.
        They can be specified by the command line parameter --query.
    """
    if "query"  in metafunc.fixturenames:
        queries = list(map(
            lambda qs:
                {param:values[1] for param, values in parse_qs(qs).items()},
            metafunc.config.option.query))
        queries += DEFAULT_QUERIES[len(queries):]
        metafunc.parametrize("query", queries)


@fixture(scope="session")
def search_url(request):
    """This is the url of the search engine to connect to.
    
    The url is passed as the parameter --url.
    """
    return request.config.getoption("--url")


@fixture(scope="session")
def secret():
    return time.time()


@fixture
def validateRequest(search_url, search_tests_url, secret):
    """Return a function to request results from the search engine.
    
    The results are validated.
    If it happens that the search engine does not provide a valid response, 
    the response is printed and an AssertionError is raised.
    """
    def validateRequest(query=DEFAULT_QUERIES[0], headers={}):
        if isinstance(query, dict):
            url = search_tests_url + "?" + urlencode(query)
        elif isinstance(query, str):
            if query.startswith(search_tests_url):
                url = search_tests_url + "?" + urlparse(query).query
            else:
                assert query.startswith(search_url)
                url = search_tests_url + query[len(search_url):]
        else:
            raise TypeError("query must be either dict or str.")
        h = {"Content-Type": "application/vnd.api+json"}
        h.update(headers)
        result = requests.get(url, headers=h)
        try:
            result_json = result.json()
        except:
            print("Requesting", query, "->", url)
            raise
        if result_json["jsonapi"]["meta"].get("secret") == secret:
            for error in result_json["errors"]:
                 meta = error.get("meta")
                 if meta:
                     print(meta.get("traceback"))
                     print(error.get("detail"))
                     print(meta.get("github-url"))
                 else:
                    print("Error:", error.get("detail"))
                 print()
            assert False, "search engine tests failed."
        return result
    return validateRequest


@fixture(scope="session")
def search_tests_url(search_url, secret):
    """The url of the search engine tests."""
    search_app = get_app(target_url=search_url, secret=secret)
    search_server = ParallelBottleServer(search_app)
    yield search_server.url
    search_server.shutdown()


@fixture(scope="session")
def max_depth(request):
    """Return a number of requests to perform at maximum.
    
    This limits the number of requests which are executed
    to get all search results.
    The can be specified by the command line parameter --max-depth.
    """
    return int(request.config.getoption("--max-depth"))
