"""
This module contains the assertions and error definitions.

Please see the specification for the errors.
- https://github.com/schul-cloud/schul_cloud_search_tests/blob/master/README.rst#specification
"""
from schul_cloud_resources_server_tests.tests.assertions import assertIsError
from schul_cloud_resources_server_tests.errors import errors
from schul_cloud_resources_api_v1.schema import get_schemas
from copy import deepcopy


ERROR_CLIENT_REQUEST = 400 # https://httpstatuses.com/400
Q = "Q" # The query string
ERROR_SERVER_RESPONSE = 409 # https://httpstatuses.com/409

ERROR = get_schemas()["error"].get_valid_examples()[0]


def get_error(error_code):
    """Return an error with the specified code."""
    error = deepcopy(ERROR)
    error["errors"][0]["status"] = str(error_code)
    error["errors"][0]["title"] = errors[int(error_code)]
    return error


def assertServerReplyIsWrong(response):
    """Make sure the response is because the server responded in an
    unspecified manner.
    """
    assert response.status_code == ERROR_SERVER_RESPONSE
    assertIsError(response, ERROR_SERVER_RESPONSE)


def assertClientRequestIsInvalid(response):
    """Make sure the response is an error in the client request.
    """
    assert response.status_code == ERROR_CLIENT_REQUEST
    assertIsError(response, ERROR_CLIENT_REQUEST)
