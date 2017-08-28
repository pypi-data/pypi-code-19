from bs4 import BeautifulSoup

from .conf import settings


def get_nav_elements(soup):
    """
    Return the list of navigation elements as set by the `NAV_ELEMENTS`
    setting, as a list of BeautifulSoup nodes.
    """
    return soup.select(settings.NAV_ELEMENTS)


def get_soup(text):
    """
    Return a BeautifulSoup object based on the given text, using the parser set
    by the `XML_PARSER` setting.
    """
    return BeautifulSoup(text, settings.XML_PARSER)
