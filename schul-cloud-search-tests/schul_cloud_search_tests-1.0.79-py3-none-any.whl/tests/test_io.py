from schul_cloud_resources_api_v1.schema import get_schemas
from pytest import mark
from schul_cloud_search_tests.tests.assertions import (
    assertIsError, ERROR_CLIENT_REQUEST, Q, ERROR_SERVER_RESPONSE, ERROR)
from pprint import pprint
import copy


@mark.parametrize("response", get_schemas()["search-response"].get_valid_examples())
def test_valid_query_is_returned(search_engine, response):
    """Valid results are passed through the search engine"""
    offset = response["links"]["self"]["meta"]["offset"]
    query = {Q:"test2", "page[offset]":str(offset)}
    result = search_engine.host(response, query).request()
    data = result.json()
    pprint(data)
    assert data == response


@mark.parametrize("response", get_schemas()["search-response"].get_invalid_examples())
def test_invalid_response_is_detected(search_engine, response):
    """Detect when the search engine returns a response
    which does not fit the schema
    """
    result = search_engine.host(response).request()
    assertIsError(result, ERROR_SERVER_RESPONSE)


@mark.parametrize("invalid_response", ["{", "", b"asd", "{}", "[]"])
def test_invalid_return_values_are_handled(search_engine, invalid_response):
    """Test that a invalid responses still create a useful output.
    
    - invalid json
    - valid json but too small
    - bytes
    """
    result = search_engine.host(invalid_response).request()
    assertIsError(result, ERROR_SERVER_RESPONSE)


@mark.parametrize("content_type", [
    "application/json", "ajhkjf", "application/vnd.api+json1"])
def test_invalid_return_header_type_is_handled(search_engine, content_type):
    """The header must be correct.
    
    Wrong headers:
    - with parameters
    - application/json
    """
    result = search_engine.host(headers={"Content-Type":content_type}).request()
    assertIsError(result, ERROR_SERVER_RESPONSE)

@mark.parametrize("code,name", [
        (400, 'Bad Request'),
        (401, 'Unauthorized'), 
        (402, 'Payment Required'),
        (405, 'Method Not Allowed'),
        (409, 'Conflict'),
        (500, 'Internal Server Error'),
        (501, 'Not Implemented'),
        (503, 'Service Unavailable'),
        (504, 'Gateway Timeout'),
    ])
def test_400_and_500_status_codes_pass_through(
        search_engine, code, name):
    """Test that the error has the right format and is passed through directly."""
    error = copy.deepcopy(ERROR)
    error["errors"][0]["status"] = str(code)
    error["errors"][0]["title"] = name
    assertIsError(error, code)
    response = search_engine.host(error, status_code=code).request()
    assert response.status_code == code
    assert error == response.json()


@mark.parametrize("code", [200, 201, 301, 466, 588])
def test_status_code_and_error_code_must_match(search_engine, code):
    """The serach engine detects of the returned error
    and the status code do not match.
    """
    result = search_engine.host(ERROR, status_code=code).request()
    assertIsError(result, ERROR_SERVER_RESPONSE)

