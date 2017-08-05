"""
This file contains the test that validates the result.


"""
from pytest import mark


def get_href(link):
    """Return the reference of the link."""
    if link is None:
        return link
    if isinstance(link, dict):
        return link.get("href")
    return link


@mark.current
def test_self_link_works_multiple_times(query, validateRequest):
    """The self link can be requested again.
    
    At least the self link should be the same.
    However here, we assume the same response is given.
    """
    first_result = validateRequest(query).json()
    href = first_result["links"]["self"]["href"]
    second_result = validateRequest(href).json()
    assert first_result == second_result


def test_linked_resources(query, validateRequest, max_depth):
    """Test that the linked resources all link to eachother."""
    results = [validateRequest(query)]
    for i in range(max_depth):
        last_result = results[-1]
        next_link = get_href(last_result.json()["links"]["next"])
        if next_link is not None:
            results.append(validateRequest(next_link))
    for self, next in zip(results, results[1:]):
        next_self = get_href(next.json()["links"]["self"])
        self_self = get_href(self.json()["links"]["self"])
        next_prev = get_href(next.json()["links"]["prev"])
        self_next = get_href(self.json()["links"]["next"])
        assert next_self == self_next, "The self link points to the next link."
        assert self_self == next_prev, "The next link points to the self link."
    last_links = set(get_href(link.json()["links"]["last"]) for link in results)
    first_links = set(get_href(link.json()["links"]["first"]) for link in results)
    assert len(first_links) == 1, "All results should have the same first link."
    assert len(last_links) == 1, "All results should have the same last link."


@mark.parametrize("sort", ["title", "title,url", "-url,title"])
def test_sorting(validateRequest, sort):
    """Test the sort parameter as described by the jsonapi.
    
    http://jsonapi.org/format/#fetching-sorting
    """
    validateRequest({"Q": "test", "sort": sort})


def test_filtering(validateRequest):
    """Test the filtering as described by the json api and search api.
    
    See
    - https://github.com/schul-cloud/resources-api-v1/#search-api
    - http://jsonapi.org/format/#fetching-filtering
    """
    validateRequest({"Q": "test", "filter[title]": "test"})
    
