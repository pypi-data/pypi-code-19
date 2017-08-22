"""
This file contains the test configuration like fixtures.
"""
from pytest import fixture
from schul_cloud_resources_server_tests.tests.fixtures import ParallelBottleServer
from bottle import Bottle, request, response
import sys
import os
import requests
from urllib.parse import urlencode
from copy import deepcopy
from schul_cloud_search_tests.tests.assertions import (
    Q, assertClientRequestIsInvalid, get_error, ERROR_CLIENT_REQUEST)
import json
from schul_cloud_resources_api_v1.schema import get_schemas
from collections import namedtuple
import pytest


HERE = os.path.dirname(__file__)
MODULE_ROOT = os.path.join(HERE, "..", "..")
try:
    import schul_cloud_search_tests
except ImportError:
    sys.path.append(MODULE_ROOT)
from schul_cloud_search_tests.proxy import get_app


DEFAULT_PARAMETERS = {"Q":"test"}
DEFAULT_HEADERS = {}
DEFAULT_STATUS_CODE = 200
JSONAPI = {
    "version": "1.0",
    "meta" : {
      "name": "Example Server",
      "source": "https://github.com/schul-cloud/resources-api-v1",
      "description": "This is a test server for the search API."
    }
}


class Requester(object):
    """Shortcut to request a hosted resource."""
    
    def __init__(self, url):
        """Create a requester."""
        self._url = url
    
    def request(self, headers={}):
        """Request the resource."""
        return requests.get(self._url, headers=headers)


def ending_with_slash(url):
    """Return the url with a slash in the end."""
    if not url.endswith("/"):
        url = url + "/"
    return url


def params_to_key(params):
    """Return a tuple key for the parameters."""
    for key, value in params.items():
        assert isinstance(key, str)
        assert isinstance(value, str)
    key = list(params.items())
    key.sort()
    return tuple(key)


class SearchEngine(object):
    """The search engine adapter.
    
    This includes:
    - the running search tests server
    - a bottle server returning the registeres responses
    """
    
    _default_response = {
      "jsonapi": JSONAPI,
      "links": {
        "self": {
          "href": None,
          "meta": {
            "count": 0,
            "offset": 0,
            "limit": 0
          }
        },
        "first": None,
        "last": None,
        "prev": None,
        "next": None
      },
      "data": []
    }

    def __init__(self):
        """Create a search engine object."""
        self._queries = {}
        self._app = Bottle()
        self._app.get("/", callback=self._serve_request)
        self._reset_servers()
    
    def start(self):
        """Start the search engine tests and the search engine mock."""
        assert not self.is_started()
        self._server = ParallelBottleServer(self._app)
        self._search_app = get_app(target_url=self.search_engine_url)
        self._search_server = ParallelBottleServer(self._search_app)
        
    @property
    def search_engine_url(self):
        """Return the URL of the mocked search engine."""
        assert self.is_started()
        return ending_with_slash(self._server.url)

    @property
    def proxy_url(self):
        """Return the url of the search engine tests proxy."""
        assert self.is_started()
        return ending_with_slash(self._search_server.url)
        
    def stop(self):
        """Stop the search engine tests and the mock server."""
        assert self.is_started()
        self._server.shutdown()
        self._search_server.shutdown()
        self._reset_servers()

    def _reset_servers(self):
        """Create the starting condition"""
        self._server = None
        self._search_server = None
        self._search_app = None

    def is_started(self):
        """Return whether the server is started."""
        return self._server is not None
        
    def host(self,
             response=None,
             params=DEFAULT_PARAMETERS,
             headers=DEFAULT_HEADERS,
             status_code=DEFAULT_STATUS_CODE):
        """Host the response given by the query.
        
        Default headers are 
        - "Content-Type": "application/vnd.api+json"
        """
        if response is None:
            response = self.get_default_response(params)
        key = params_to_key(params)
        print("host:", key, file=sys.stderr)
        assert key not in self._queries
        self._queries[key] = (response, headers, status_code)
        return self._new_requester(params)
    
    def clear(self):
        """Remove all hosted responses."""
        self._queries = {}
        self._last_response = None
        self._last_request_headers = None

    def _serve_request(self):
        """Serve a request to the search engine bottle server."""
        default = object()
        key = params_to_key(request.query)
        print("request:", key, file=sys.stderr)
        self._last_request_headers = dict(request.headers)
        result = self._queries.get(key, default)
        if result is default:
            json_response = self.get_default_response(request.query_string)
            headers = DEFAULT_HEADERS
            status_code = DEFAULT_STATUS_CODE
            print("Return default result.", file=sys.stderr)
        else:
            json_response, headers, status_code = result
        self._last_response = json_response
        default_headers = {"Content-Type": "application/vnd.api+json"}
        default_headers.update(headers)
        for header, value in default_headers.items():
            response.set_header(header, value)
        response.status = status_code
        if isinstance(json_response, dict):
            return json.dumps(json_response).encode("UTF-8")
        return json_response

    def request(self,
                params=DEFAULT_PARAMETERS,
                headers=DEFAULT_HEADERS):
        """Request a search with parameters."""
        return self._new_requester(params).request(headers)
        
    def _new_requester(self, params):
        """Return a new Requester object from the parameters."""
        request_url = self.proxy_url + "?" + urlencode(params)
        return Requester(request_url)
        
    def get_default_response(self, query):
        """Return the default response to a query.
        
        The query can be given as string or as dict.
        """
        if not isinstance(query, str):
            query = urlencode(query)
        result = deepcopy(self._default_response)
        url = self.search_engine_url + "?" + query
        result["links"]["self"]["href"] = url
        return result
        
    @property
    def last_response(self):
        """Return the last reponse of the search engine to a request.
        
        If there was no request, None is returned.
        """
        return self._last_response

    @property
    def last_request_headers(self):
        """Return the last request headers of the search engine in a request.
        
        If there was no request, None is returned.
        """
        return self._last_request_headers


@fixture(scope="session")
def search_engine_session():
    """Return the server to store resources."""
    server = SearchEngine()
    server.start()
    yield server
    server.stop()


@fixture
def search_engine(search_engine_session):
    """Return a fresh server object with no resources."""
    search_engine_session.clear()
    yield search_engine_session
    search_engine_session.clear()


@fixture
def code_url(search_engine):
    """Return the url of the code enpoint."""
    return search_engine.proxy_url + "code"


VALID_RESOURCE = get_schemas()["resource"].get_valid_examples()[0]
@fixture
def valid_resource():
    """Return a valid resource."""
    return {"type": "resource", "attributes": deepcopy(VALID_RESOURCE), "id": "1"}


@fixture(params=[11, 20])
def limit(request):
    """Return the limit of one search request."""
    return request.param


@fixture(params=[0, 8, 100])
def link_resources(request, valid_resource, limit):
    """Return a list of resources wich are returned by a search."""
    result = [[]]
    count = 0
    count_in_last_request = 0
    while count < request.param:
        if count_in_last_request >= limit:
            result.append([])
            count_in_last_request = 0
        result[-1].append(valid_resource)
        count += 1
        count_in_last_request += 1
    return result


@fixture
def link_parameters(link_resources, limit):
    """Return the parameters used to search."""
    result = [{Q:"tralala"}]
    count = len(link_resources[0])
    for res in link_resources[1:]:
        result.append({Q:"tralala", "page[limit]":str(limit), "page[offset]":str(count)})
        count += len(res)
    return result


@fixture
def link_urls(search_engine, link_parameters):
    """Return a list of links for the paramaters"""
    return [search_engine.search_engine_url + "?" + urlencode(params)
            for params in link_parameters]


@fixture
def link_responses(link_urls, link_parameters, link_resources, limit):
    """Return a response with filled links.
    
    The response is not hosted by the search engine.
    """
    result = []
    offset = 0
    for url, parameters, resources, next_url, previous_url in zip(
            link_urls, link_parameters, link_resources,
            link_urls[1:] + [None], [None] + link_urls[:-1]):
        response = {
          "jsonapi": JSONAPI,
          "links": {
            "self": {
              "href": url,
              "meta": {
                "count": len(resources),
                "offset": offset,
                "limit": limit,
              }
            },
            "first": (link_urls[0] if resources else None),
            "last": (link_urls[-1] if resources else None),
            "prev": previous_url,
            "next": next_url,
          },
          "data": resources,
        }
        result.append(response)
        offset += len(resources)
    return result

LinkedRequest = namedtuple("LinkedRequest", [
    "resources", "parameters", "url", "response", "request"])

@fixture
def link_request(search_engine, link_parameters, link_responses):
    """Return a list of requesters for the responses."""
    return [search_engine.host(response, parameters).request
            for response, parameters in zip(link_responses, link_parameters)]


@fixture
def linked_search(link_responses, link_urls, link_parameters, link_resources, 
          link_request):
    """Return a list of linked resource requests.
    
    Each element has the following attributes:
    - response
    - url
    - paramaters
    - resources
    """
    return list(map(lambda t: LinkedRequest(*t), zip(link_resources, link_parameters, link_urls, link_responses, link_request)))


@fixture
def first_search(linked_search):
    """The first of the linked searches."""
    return linked_search[0]


@fixture
def second_search(linked_search):
    """The second of the linked searches."""
    if len(linked_search) < 2:
        pytest.skip("Not enough searches with a limit.")
    return linked_search[1]


@fixture
def third_search(linked_search):
    """The third of the linked searches."""
    if len(linked_search) < 3:
        pytest.skip("Not enough searches with a limit.")
    return linked_search[2]


@fixture
def last_search(linked_search):
    """The last of the linked searches."""
    return linked_search[-1]


@fixture
def high_offset_search(last_search, first_search):
    """Return a search with an offset which is too high."""
    if last_search == first_search:
        pytest.skip("need mutiple searches")
    last_search.response["data"] = []
    last_search.response["links"]["self"]["meta"]["count"] = 0
    last_search.response["links"]["next"] = None
    last_search.response["links"]["prev"] = None
    last_search.response["links"]["last"] = None
    last_search.response["links"]["first"] = None
    return last_search


@fixture
def not_last_search(first_search, last_search):
    """Return a search which is definitely not the last search."""
    if first_search == last_search:
        pytest.skip("I need a request that is not the last.")
    return first_search


@fixture(params=[
        get_error(ERROR_CLIENT_REQUEST),
        None
    ])
def response400(request):
    """Return the response which yeilds a 400 by the proxy."""
    return request.param


@fixture
def assertIs400(response400):
    """Return an assertion function which tests that the result is correct."""
    if response400 is None:
        return assertClientRequestIsInvalid
    else:
        def test_error_passes_through(response):
            """Make sure the error passes through."""
            response = response.json()
            print("response:", response)
            print("response400:", response400)
            assert response == response400
        return test_error_passes_through


@fixture
def request400(search_engine, response400):
    """Return a function that requests parameters."""
    return lambda params: search_engine.host(response=response400, params=params, status_code=(200 if response400 is None else 400)).request()
