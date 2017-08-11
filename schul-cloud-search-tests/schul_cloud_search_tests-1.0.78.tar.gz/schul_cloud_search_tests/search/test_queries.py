"""
This file provides the tests which should be run against a running search engine.

You can view examples of such tests in the Issue 6.
    https://github.com/schul-cloud/schul_cloud_search_tests/issues/6

The idea is to use these tests to verify the behavior of the search api.
    https://github.com/schul-cloud/resources-api-v1#search-api
"""
from schul_cloud_search_tests.tests.test_request import (
    MALFORMED_PARAMETERS)
from pytest import mark


def test_q_is_missing(validateRequest):
    """Request a search with the q parameter missing."""
    validateRequest({})


@mark.parametrize("parameter", [parameter for 
                                parameter, parameter_is_valid in
                                MALFORMED_PARAMETERS if not parameter_is_valid])
def test_malformed_parameters(validateRequest, parameter):
    """Test that the list of malformed parameters results in a 400 answer."""
    validateRequest({parameter:"0"})


@mark.parametrize("param", ["page[offset]", "page[limit]"])
@mark.parametrize("value", ["", "asd", "-1"])
def test_invalid_paramater_values(validateRequest, param, value):
    """Test that the search engine recognizes invalid parameters.
    
    The answer 400 is expected.
    """
    validateRequest({param:"0"})











