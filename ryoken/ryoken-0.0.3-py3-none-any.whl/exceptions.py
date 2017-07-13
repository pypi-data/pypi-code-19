class CompromisedToken(Exception):
    """
    Raised if the token has been compromised.
    """

    def __init__(self):
        super().__init__("The sign doesn't match the given contents. The token has been compromised.")


class UnexpectedJsonData(Exception):
    """
    Raised if a non string argument is given to the json decode method.
    """
    def __init__(self):
        super().__init__("The decode method only supports string arguments.")


class JsonDecodeError(ValueError):
    """
    Raised if the provided json data couldn't be decoded due to a syntaxis error.
    """
    def __init__(self):
        super().__init__("uJSON couldn't decode the provided data due to a syntaxis error.")


class UnexpectedDataValue(Exception):
    """
    Raised if the given data argument isn't a list nor a tuple.
    """
    def __init__(self):
        super().__init__("The data argument must be a list or a tuple.")
