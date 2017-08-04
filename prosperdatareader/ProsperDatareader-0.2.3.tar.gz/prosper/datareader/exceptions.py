"""exceptions.py: collection of exceptions for Datareader libraries"""

class DatareaderException(Exception):
    """base class for Datareader exceptions"""
    pass
class DatareaderWarning(UserWarning):
    """base class for Datareader warnings"""
    pass
class PaginationWarning(DatareaderWarning):
    """hard limit reached for recursive page diving"""
    pass

############
## Stocks ##
############
class StocksException(DatareaderException):
    """base class for Datareader.stocks"""
    pass
class StocksPricesException(StocksException):
    """base class for Datareader.stocks.prices"""
    pass


class StocksNewsException(StocksException):
    """base class for Datareader.stocks.prices"""
    pass
