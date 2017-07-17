class CensusError(Exception):
    """Superclass for errors in the uscensus API wrapper library.
    """
    pass


class DBError(CensusError):
    """Class for reporting database errors in the uscensus API wrapper
    library.
    """
    pass
