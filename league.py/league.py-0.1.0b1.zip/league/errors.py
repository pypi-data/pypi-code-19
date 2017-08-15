class NoMatchFound(Exception):
    """Exception thrown when a match does not return any data,
    usually indicating the match was not found or invalid data was passed.
    """

    def __init__(self):
        super().__init__("No Match found")


class NoSummonerFound(Exception):
    """Exception thrown if a summoner-lookup fails"""

    def __init__(self):
        super().__init__("No Summoner Found")


class UnAuthorized(Exception):
    """
    This error indicates that the API request being made did not contain the necessary authentication credentials
    and therefore the client was denied access.
    If authentication credentials were already included then the Unauthorized response indicates that authorization
    has been refused for those credentials. In the case of the API, authorization credentials refer to your API key.

    """

    def __init__(self):
        super().__init__("Invalid API key")


class BadRequest(Exception):
    """
    This error indicates that there is a syntax error in the request and the request has therefore been denied.
    The client should not continue to make similar requests without modifying the syntax or the requests being made.

    """

    def __init__(self):
        super().__init__("Bad Request")


class EmptyResponse(Exception):
    """This error indicates that the server has not found a match for the API request being made.
    No indication is given whether the condition is temporary or permanent.
    Common Reasons:

    * The ID or name provided does not match any existing resource (e.g., there is no summoner matching the specified ID)
    * The API request was for an incorrect or unsupported path
"""

    def __init__(self):
        super().__init__("API returned no results")


class RateLimited(Exception):
    """
    This error indicates that the application has exhausted its maximum number of
    allotted API calls allowed for a given duration.

    Attributes
    ----------
    cooldown : int
        The amount of seconds before the cooldown is exhausted

    """

    def __init__(self, cooldown):
        self.cooldown = cooldown
        super().__init__("Rate Limited for {0} seconds".format(cooldown))


class ServiceUnavailable(Exception):
    """
    This error indicates the server is currently unavailable to handle requests because of an unknown reason.
    The Service Unavailable response implies a temporary condition which will be alleviated after some delay.

    """

    def __init__(self):
        super().__init__("Service temporally unavailable, try again later")


class InvalidRegionType(Exception):
    """
    This exception is raised when attempting to request data from a non existent/invalid region type.

    """

    def __init__(self):
        super().__init__("Invalid Region passed")


class InactivePlayer(Exception):
    """
    This exception is raised when Player exists, but hasn't played since match history collection began
    """

    def __init__(self):
        super().__init__("No data returned on player")
