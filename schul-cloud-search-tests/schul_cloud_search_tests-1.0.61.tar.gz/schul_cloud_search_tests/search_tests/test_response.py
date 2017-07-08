"""
Each test function here covers a part of the specification.
They are run when the server returns a request.
If they fail, the client gets feedback.

About the test functions:
Please provide
- A short description of what is tested
- Links to the specification, where this is specified.

"""
from pytest import mark
from schul_cloud_resources_api_v1.schema import get_schemas
from schul_cloud_resources_server_tests.tests.assertions import assertIsError


def test_result_is_json(result):
    """Make sure the result is a json object.
    
    See
    - http://jsonapi.org/"""
    try:
        json = result.json()
    except:
        assert False, "The result must be a valid json object, not {}".format(result.content)
    else:
        assert isinstance(json, dict), "The result must be a json object, not {}".format(json)


def test_response_schema(search_response):
    """If the request was successful, it must match the search-response schema.
    
    Schema:
    - https://github.com/schul-cloud/resources-api-v1/tree/master/schemas/search-response
    
    The response is successful of a status code 200 is returned.
    """
    schema = get_schemas()["search-response"]
    schema.validate(search_response)
    

def test_400_and_500_status_codes_have_the_jsonapi_design(error, result):
    """If the status code is 4XX, it contains a list of errors.

    Schema:
    - https://github.com/schul-cloud/resources-api-v1/tree/master/schemas/error
    """
    assertIsError(error, result.status_code)
    

def test_the_content_type_is_from_the_jsonapi(result):
    """Make sure the returned content type is specified and expected.
    
    See here:
    - http://jsonapi.org/format/#content-negotiation-clients
    """
    assert result.headers.get("Content-Type", "") == "application/vnd.api+json", "The content type of the server reply must be application/vnd.api+json."


def test_406_error_is_expected_in_case_of_invalid_accept_headers(
        search, result, json):
    """If the client does not acccept application/vnd.api+json, 
    Error 406 should be returned.

    See
    - http://jsonapi.org/format/#content-negotiation-servers
    """
    accept = search.headers.get("Accept", None)
    if accept is None: return
    accepted_content_types = accept.split(",")
    print("Accepted content types:", accepted_content_types)
    possible_content_types = ["*/*", "application/*", "application/vnd.api+json"]
    content_type_is_accepted = any(
        possible_content_type in accepted_content_types
        for possible_content_type in possible_content_types)
    must_be_406 = not content_type_is_accepted
    is_406 = result.status_code == 406
    assert is_406 == must_be_406, "Error 406 is returned only if the content type is not accepable."
