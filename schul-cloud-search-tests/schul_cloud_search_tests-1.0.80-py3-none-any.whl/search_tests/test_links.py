"""
Each test function here covers a part of the specification.
They are run when the server returns a request.
If they fail, the client gets feedback.

About the test functions:
Please provide
- A short description of what is tested
- Links to the specification, where this is specified.

These test functions all relate to the "links" attribute of the search response.
- https://github.com/schul-cloud/resources-api-v1/tree/master/schemas/search-response#search-reponse-1

"""
from pytest import mark
from urllib.parse import parse_qs, urlparse


def get_offset(link):
    """Return the offset from a link."""
    query = parse_qs(urlparse(get_href(link)).query)
    return int(query.get("page[offset]", [0])[0])


def get_href(link):
    """Return the href of the link."""
    if link is None:
        return None
    if isinstance(link, dict):
        return link.get("href")
    assert isinstance(link, str), "a link must be either a string or an object."
    return link


def test_count_is_less_or_equal_to_the_limit(self_link):
    """The limit is the maximum number of objects returned.
    """
    assert self_link["meta"]["count"] <= self_link["meta"]["limit"]


def test_limit_may_be_reduced(self_link, limit):
    """If the limit is higher than the maximum limit the server has internally, the server sets the limit to the maximum available limit.
    """
    assert limit is None or self_link["meta"]["limit"] <= limit


def test_count(self_link, search_response, data):
    """count is the actual number of objects retrieved.
    
    The count must be equal to the number of objects in the list.
    """
    assert len(data) == self_link["meta"]["count"]


def test_offset(self_link, offset):
    """offset is the start index in the list of objects.
    
    The offset must be the same as requested.
    When a query is done without offset, the requested offset is zero.
    """
    assert self_link["meta"]["offset"] == offset


def test_the_end_is_reached(self_link, links):
    """If the end of the resource list is reached, count may be less than limit.
    
    This implies that 
    - there is no next link and 
    - if there are resources, the last link is self 
    - if there are no resources in this request
      - the last link is pointing to a lesser offset or
      - the last link is null
    """
    if self_link["meta"]["count"] and \
            self_link["meta"]["count"] < self_link["meta"]["limit"]:
        assert links["next"] is None
        assert self_link["href"] == get_href(links["last"])
    elif self_link["href"] == get_href(links["last"]):
        assert links["next"] is None


def test_no_resources_given(search_response, links, offset):
    """If there are no resources, first, last, prev and next MUST be null.
    """
    if len(search_response["data"]) == 0:
        if offset == 0:
            assert links["last"] is None
            assert links["first"] is None
        assert links["prev"] is None
        assert links["next"] is None


def test_last_implies_next(links, offset):
    """If links["last"] is given, links["next"] must be given.

    This only works if this is not the last request, becuase
    the last request has no next request.
    """
    if links["last"] and get_offset(links["last"]) > offset:
        print("last offset:", get_offset(links["last"]))
        assert links["next"] is not None, "The next link must be given if self is before the last link."


def test_first_implies_prev(links, offset):
    """If first is given, prev must be given.
    
    This is only valid, if we did not request an offset which is out of range.
    """
    if links["first"] and links["last"] \
            and get_offset(links["last"]) > offset > 0:
        assert links["prev"] is not None, "The prev link must be given if there is a first link and the request is not out of range."


def test_next_does_not_skip_objects(links, self_link):
    """The next link MUST not skip objects.
    
    This can only be inferred by the limit and offset.
    """
    if links["next"]:
        next_offset = get_offset(links["next"])
        self_offset = self_link["meta"]["offset"]
        limit = self_link["meta"]["limit"]
        assert next_offset == self_offset + limit, "The offset of the next link must be increased by the limit."
        

def test_prev_does_not_skip_objects(links, self_link):
    """The prev link MUST not skip objects.
    
    This can only be inferred by the limit and offset.
    """
    if links["prev"]:
        prev_offset = get_offset(links["prev"])
        self_offset = self_link["meta"]["offset"]
        limit = self_link["meta"]["limit"]
        assert prev_offset == self_offset - limit, "The offset of the prev link must be decreased by the limit."


@mark.parametrize("link_name", ["prev", "next", "last", "first", "self"])
def test_links_are_absolute(link_name, links):
    """All links are absolute links using the host header field.
    """
    href = get_href(links[link_name])
    if href is not None:
        link_scheme = urlparse(href).scheme
        print("link_scheme:", repr(link_scheme), href)
        assert link_scheme in ["http", "https"], "there must be a scheme like http:// in the url for {}, not {} in ".format(link_name, repr(link_scheme))


def test_request_too_far(links, offset, self_link, data):
    """Requesting beyond the last link yields no objects.
    
    A request beyond the last possible request yields no objects.
    """
    limit = self_link["meta"]["limit"]
    if links["last"] and get_offset(links["last"]) + limit <= offset:
        assert len(data) == 0, "No data should be given but {} objects were found.".format(len(data))
