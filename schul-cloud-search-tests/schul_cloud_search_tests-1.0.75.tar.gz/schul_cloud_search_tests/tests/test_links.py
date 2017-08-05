"""These tests test the links which are available.

"""
from pytest import mark
import copy
from schul_cloud_search_tests.tests.assertions import (
    assertServerReplyIsWrong)
from pprint import pprint
import pytest


def test_correct_self_link_is_passed_through(linked_search):
    """Test that the linked search passes through the search engine."""
    for search in linked_search:
        result = search.request().json()
        response = search.response
        print("result:  ", result)
        print("response:", response)
        assert result == response


def test_the_first_response_must_have_the_offest_0(linked_search):
    """The first request is done without specifying an offset.
    The offset 0 is implied."""
    linked_search[0].response["links"]["self"]["meta"]["offset"] = 1
    assertServerReplyIsWrong(linked_search[0].request())


def test_the_limit_may_be_reduced_by_the_server(
        second_search, search_engine, limit):
    """The server can reduce the limit."""
    response = second_search.response
    second_search.parameters["page[limit]"] = str(limit + 1)
    result = search_engine.host(
         second_search.response, second_search.parameters
         ).request().json()
    assert result == response


def test_the_limit_can_not_be_increased_by_the_server(second_search):
    """The server may not increase the limit."""
    second_search.response["links"]["self"]["meta"]["limit"] += 1
    assertServerReplyIsWrong(second_search.request())
    

def test_count_does_not_match(first_search):
    """count must be equal t the number of objects."""
    first_search.response["links"]["self"]["meta"]["count"] += 1
    assertServerReplyIsWrong(first_search.request())


def test_count_can_not_be_greater_than_the_limit(first_search):
    """We reduce the limit so it is smaller than the count. This must be wrong."""
    first_search.response["links"]["self"]["meta"]["limit"] = \
        first_search.response["links"]["self"]["meta"]["count"] - 1
    assertServerReplyIsWrong(first_search.request())
    

def test_count_must_equal_limit_for_links_in_between(not_last_search):
    """If a search is not the last, the count must be equal to the limit.
    
    Test that
    - last last link is self
    """
    response = not_last_search.response
    response["data"].pop()
    links = response["links"]
    meta = links["self"]["meta"]
    meta["count"] -= 1
    links["next"] = None
    assert links["self"]["href"] != links["last"], "precondition for the test"
    assertServerReplyIsWrong(not_last_search.request())


def test_next_link_of_last_request_must_be_null(last_search):
    """If the next link is set in the last request, it is an error."""
    last_search.response["links"]["next"] = \
        last_search.response["links"]["self"]["href"]
    print('last_search.response["links"]:', last_search.response["links"])
    assertServerReplyIsWrong(last_search.request())


@mark.parametrize("link_name", ["first", "last", "prev", "next"])
def test_no_resources_imply_no_links_to_other_searches(first_search, link_name):
    if len(first_search.resources) != 0:
        pytest.skip("Need something with no resources")
    first_search.response["links"][link_name] = \
        first_search.response["links"]["self"]["href"]
    print(first_search.response)
    assertServerReplyIsWrong(first_search.request())


@mark.parametrize("link_name", ["first", "last"])
def test_search_with_offset_too_high_can_have_links(high_offset_search, first_search, link_name):
    """If a search requests an offset too high,
    the first and the last link may be set.
    """
    high_offset_search.response["links"][link_name] = \
        first_search.response["links"]["self"]["href"]
    result = high_offset_search.request().json()
    response = high_offset_search.response
    assert result == response, "search results with too high offset are passed through"


@mark.parametrize("link_name", ["prev", "next"])
def test_search_with_offset_too_high_can_not_have_links(high_offset_search, first_search, link_name):
    """If a search requests an offset too high,
    the prev and the next link can not be set.
    """
    high_offset_search.response["links"][link_name] = \
        first_search.response["links"]["self"]["href"]
    assertServerReplyIsWrong(high_offset_search.request())


def test_last_link_implies_next_link_for_all_but_last_request(
        not_last_search):
    """A last link is given: we test that the next link must exist."""
    assert not_last_search.response["links"]["last"], "precondition for the test"
    not_last_search.response["links"]["next"] = None
    assertServerReplyIsWrong(not_last_search.request())


def test_first_implies_prev_link_for_all_but_first_request(second_search):
    """If the first link is given, also a prev link must be given.
    
    This is only valid, if we did not request an offset which is out of range.
    """
    assert second_search.response["links"]["first"], "precondition for the test"
    second_search.response["links"]["prev"] = None
    assertServerReplyIsWrong(second_search.request())
    

def test_next_link_does_not_skip_objects(first_search, second_search):
    """The next link must follow directly."""
    first_search.response["links"]["next"] = second_search.response["links"]["next"]
    assertServerReplyIsWrong(first_search.request())


def test_prev_link_does_not_skip_objects(second_search, third_search):
    """The prev link must precede directly."""
    third_search.response["links"]["prev"] = second_search.response["links"]["prev"]
    assertServerReplyIsWrong(third_search.request())


def test_href_object_links_are_ok_for_the_search(linked_search):
    """If the links are given, the search must be ok with the href."""
    for search in linked_search:
        response = search.response
        for link_name in ["next", "prev", "first", "last"]:
            if response["links"][link_name]:
                response["links"][link_name] = {
                    "href":response["links"][link_name],
                    "meta": {}}
        result = search.request().json()
        print("result:  ", result)
        print("response:", response)
        assert result == response


@mark.parametrize("link_name", ["self", "prev", "first", "last", "next"])
def test_relative_links_are_not_allowed(second_search, third_search, link_name):
    """Test that the links must start with http or https."""
    existing_link = second_search.response["links"][link_name]
    START = "http://"
    if isinstance(existing_link, str):
        assert existing_link.startswith(START)
        new_link = existing_link[len(START):]
        second_search.response["links"][link_name] = new_link
    if isinstance(existing_link, dict):
        assert existing_link['href'].startswith(START)
        new_link = existing_link['href'][len(START):]
        existing_link['href'] = new_link
    assertServerReplyIsWrong(second_search.request())


def test_requests_beyond_the_last_must_not_have_objects(
        first_search, second_search):
    """A request beyond the last link, there shall be no objects to return.
    
    Make the second search look like the last.
    """
    second_search.response["links"]["next"] = None
    second_search.response["links"]["prev"] = None
    second_search.response["links"]["last"] = first_search.response["links"]["first"]
    assertServerReplyIsWrong(second_search.request())
