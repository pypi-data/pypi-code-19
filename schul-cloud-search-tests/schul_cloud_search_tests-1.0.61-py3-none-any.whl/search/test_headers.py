"""
Test the headers of search requests.
"""


from schul_cloud_search_tests.tests.test_headers import (
    INVALID_ACCEPT_HEADERS)
from pytest import mark


@mark.parametrize("invalid_accept_header", INVALID_ACCEPT_HEADERS)
def test_detect_invalid_accept_headers(validateRequest, invalid_accept_header):
    validateRequest(headers={"Accept":invalid_accept_header})


