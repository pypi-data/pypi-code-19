"""
Each test function here covers a part of the specification.
All tests in here should be marked by 

    @mark.request

They are run on the clients request.
If they fail, the client gets feedback and the server does not get the request.

About the test functions:
Please provide
- A short description of what is tested
- Links to the specification, where this is specified.

"""
from pytest import mark
import pytest
import re


@mark.request
def test_request_has_query(params):
    """Test that the query includes a "Q".
    
    This is specified here:
    - https://github.com/schul-cloud/resources-api-v1/#search-api
    """
    assert params.get("Q") is not None, (
        "Please pass a query string to with Q=... to the request.")


@mark.request
@mark.parametrize("parameter", ["page[offset]", "page[limit]"])
def test_integer_parameters(params, parameter):
    """Test that page[offset] and page[limit] are positive integers.
    
    This is specified here:
    - https://github.com/schul-cloud/resources-api-v1/#search-api
    """
    value = params.get(parameter)
    if value is None:
        pytest.skip("parameter {} absent".format(parameter))
    assert value.isdigit(), (
        "The parameter {} must be a positive integer, not {}."
        .format(parameter, value))
    

JSONAPI_ATTRIBUTE = re.compile("^(sort|filter\\[.+\\]|page\\[(offset|limit)\\])$")


@mark.request
def test_all_parameter_names_are_jsonapi_compatible(params):
    """If search engines add new parameters, they MUST be jsonapi compatible.
    
    See jsonapi
    - http://jsonapi.org/format/#query-parameters
    
    This includes:
    - parameter names
    - filter[ATTRIBUTE.XX.YY....]
    """
    for parameter in params:
        assert parameter, "The parameter must be named \"{}\".".format(parameter)
        for character in (parameter[0], parameter[-1]):
            assert character not in ["-", "_", " "], "Additionally, the following characters are allowed in member names, except as the first or last character: U+002D HYPHEN-MINUS, “-“, U+005F LOW LINE, “_”, and U+0020 SPACE, “ “ (not recommended, not URL safe)"
        has_non_az_character = False
        is_jsonapi_parameter = bool(JSONAPI_ATTRIBUTE.match(parameter))
        for character in parameter:
            assert is_jsonapi_parameter or character not in '+,.[]!"#$%&\'()*/:;<=>?@\\^`{|}~\x7f\x00\x1f', "The following characters MUST NOT be used in member names: " + '\'+\', \',\', \'.\', \'[\', \']\', \'!\', \'"\', \'#\', \'$\', \'%\', \'&\', "\'", \'(\', \')\', \'*\', \'/\', \':\', \';\', \'<\', \'=\', \'>\', \'?\', \'@\', \'\\\\\', \'^\', \'`\', \'{\', \'|\', \'}\', \'~\', \'\\x7f\', \'\\x00\', \'\\x1f\''
            has_non_az_character = has_non_az_character or character < "a"
            has_non_az_character = has_non_az_character or "z" < character
        assert is_jsonapi_parameter or has_non_az_character, "Implementation specific query parameters MUST adhere to the same constraints as member names with the additional requirement that they MUST contain at least one non a-z character (U+0061 to U+007A). Parameter \"{}\"".format(parameter)
