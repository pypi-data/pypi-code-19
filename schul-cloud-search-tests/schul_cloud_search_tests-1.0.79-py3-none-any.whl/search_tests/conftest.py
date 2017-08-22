"""
Run tests for the requests and responses.

If you mark your test with
@pytest.mark.request
your test is executed when the request arrives.

"""

from pytest import fixture, hookimpl
import pytest
from schul_cloud_search_tests.search_tests import (
    get_response, add_failing_test, get_request_url
)
import pytest


try:
    pytest.skip()
except Exception as e:
    SKIP_ERROR = e.__class__


@fixture
def search():
    """The request to the server.
    
    The request from the client
    - http://bottlepy.org/docs/dev/api.html#bottle.BaseRequest
    """
    from bottle import request
    return request


@fixture
def result():
    """The response to the query.
    
    The response from the server.
    - http://docs.python-requests.org/en/master/api/#requests.Response
    """
    return get_response()


@fixture
def json(result):
    """Return the response as json."""
    try:
        return result.json()
    except:
        pytest.skip("The result is not a valid json object. {}"
                           .format(result.content))


@fixture
def search_response(json, result):
    """Return the search response."""
    if not result.ok:
        pytest.skip("This is not a search response.")
    return json


@fixture
def error(json, result):
    """Return the error response."""
    if result.ok:
        pytest.skip("This is not an error response.")
    return json


@fixture
def search_url():
    """The url of the server to request searches from."""
    return get_request_url()


@fixture
def params(search):
    """The query parameters.
    
    The search request parameters:
    - http://bottlepy.org/docs/dev/api.html#bottle.FormsDict
    
    You can use params.get("q") to get the "q" parameter.
    """
    return search.query


@fixture
def offset(params):
    """Return the requested offset."""
    return int(params.get("page[offset]", "0"))


@fixture
def limit(params):
    """Return the requested limit."""
    limit = params.get("page[limit]")
    return (None if limit is None else int(limit))


@fixture
def links(search_response):
    """Return the links of the search response."""
    return search_response["links"]


@fixture
def self_link(links):
    """Return the self link."""
    return links["self"]


@fixture
def data(search_response):
    """Return the data field of the search response."""
    return search_response["data"]

@hookimpl(hookwrapper=True)
def pytest_pyfunc_call(pyfuncitem):
    # From
    # - https://docs.pytest.org/en/latest/writing_plugins.html#conftest-py-plugins
    # Also see 
    # - https://docs.pytest.org/en/latest/_modules/_pytest/vendored_packages/pluggy.html#_CallOutcome
    # for outcome
    
    outcome = yield
    # outcome.excinfo may be None or a (cls, val, tb) tuple
    if outcome.excinfo is not None and outcome.excinfo[0] not in (SKIP_ERROR,):
        add_failing_test(*outcome.excinfo)
    res = outcome.get_result()
