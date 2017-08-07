class OutcryError(Exception):
    """Error during Outcry validation"""
    pass


class OutcryMissingKeyError(OutcryError):
    pass


class OutcryUnexpectedTypeError(OutcryError):
    pass


class OutcryValueError(OutcryError):
    pass
