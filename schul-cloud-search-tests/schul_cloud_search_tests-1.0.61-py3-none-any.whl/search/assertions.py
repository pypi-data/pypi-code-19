"""
This file contains the assertions for the search tests.
"""
from schul_cloud_search_tests.tests.assertions import (
    assertClientRequestIsInvalid)


def assertSearchEngineExitedWith400(response):
    """Make sure that the response is from the client and not the tests.
    
    The error should be 400.
    """


