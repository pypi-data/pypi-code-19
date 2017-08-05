from pytest import mark
from schul_cloud_search_tests.tests.assertions import (
    assertIsError, ERROR_SERVER_RESPONSE, ERROR)
import copy
from pprint import pprint

INVALID_ACCEPT_HEADERS = [
        "application/vnd.api+json; v=1",
        "application/json",
        "application/json,application/vnd.api+json; v=1,",
        "image/jpeg",
        ""
    ]


@mark.parametrize("invalid_accept_header", INVALID_ACCEPT_HEADERS)
def test_detect_invalid_accept_headers(
        search_engine, invalid_accept_header):
    """Test that the server responds to invalid media type queries.
    
    This test currently only tests that the server MUST send a 406 error
    if the media type application/vnd.api+json is not accepted by the client.
    Usually, an other media type is also allowed to change the result,
    e.g. application/xml or application/json.
    This test assumes that the server speaks only application/vnd.api+json.
    
    See
    - http://jsonapi.org/format/#content-negotiation-servers
    
    The server responds with 200 but 406 is expected.
    """
    result = search_engine.request(headers={"Accept":invalid_accept_header})
    assertIsError(result, ERROR_SERVER_RESPONSE)


@mark.parametrize("invalid_accept_header", INVALID_ACCEPT_HEADERS)
def test_server_responds_with_406_and_is_passed_through(
        search_engine, invalid_accept_header):
    """When the client requests invalid headers, a 406 is passed through.
    """
    error406 = copy.deepcopy(ERROR)
    error406["errors"][0]["status"] = "406"
    error406["errors"][0]["title"] = "Not Acceptable"
    response = search_engine.host(error406, status_code=406).request(
                   headers={"Accept":invalid_accept_header})
    result = response.json()
    assert result == error406


@mark.parametrize("valid_accept_header", [
        "application/vnd.api+json; v=1,application/vnd.api+json,application/json",
        "application/vnd.api+json,application/json",
        "application/vnd.api+json",
        "application/*",
        "*/*",
    ])
def test_allow_list_of_accept_headers(search_engine, valid_accept_header):
    """If a list of accept headers is passed to the server, it can accept.
    
    The client may pass a list of media type parameters to the server.
    The server finds out that a valid parameter is included.
    See
    - http://jsonapi.org/format/#content-negotiation-servers
    """
    response = search_engine.request(headers={"Accept":valid_accept_header})
    result = response.json()
    assert result == search_engine.last_response


@mark.parametrize("headers", [
        {"Xsss": "23423"},
        {"Accept": "application/json"},
        {"Authorization": "basic basic===", "X-Asd": "22"},
    ])
def test_search_engine_passes_headers_through(search_engine, headers):
    """Test that certain headers pass through the proxy.
    
    """
    search_engine.request(headers=headers)
    for key, value in headers.items():
        assert search_engine.last_request_headers[key] == value


@mark.parametrize("headers", [
        {"Content-Type": "application/vnd.api+json; charset=UTF-8"},
        {"Content-Type": "application/vnd.api+json; Y2736487=sdfsdf"},
        {"Content-Type": "application/vnd.api+json; charset=UTF-8,jsdhfgaskfgdskgfkjas"},
        {"Content-Type": "application/vnd.api+json; charset=UTF-8sjhfkjafsd"},
        {"Test-Header": "123"}
    ])
def test_response_content_type_headers_are_accepted(search_engine, headers):
    """Make sure that different returned content types are accepted by the proxy.
    
    See Issue 11
        https://github.com/schul-cloud/schul_cloud_search_tests/issues/11
    
    > Clients MUST ignore any parameters for the application/vnd.api+json media type received in the Content-Type header of response documents.
    - http://jsonapi.org/format/#content-negotiation-clients
    """
    response = search_engine.host(headers=headers).request()
    result = response.json()
    pprint(result)
    assert result == search_engine.last_response
    for key, value in headers.items():
        assert response.headers[key] == value


