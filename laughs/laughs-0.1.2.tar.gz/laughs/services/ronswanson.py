"""
    ronswanson.py
    ~~~~~~~~~~~~~

    Get and return jokes from ron-swanson-quotes

    :copyright: (c) 2017 by Sean Callaway.
    :license: MIT, see LICENSE for more details.
"""
import requests
import json

def get_joke():
    """Return a Ron Swanson quote.

    Returns None if unable to retrieve a quote.
    """

    page = requests.get("http://ron-swanson-quotes.herokuapp.com/v2/quotes")
    
    if page.status_code == 200:
        jokes = []
        jokes = json.loads(page.content.decode(page.encoding))
        return '"' + jokes[0] + '" - Ron Swanson'

    return None
