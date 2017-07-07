"""
    dadjokes.py
    ~~~~~~~~~~~

    Get and return jokes from icanhazdadjoke.com

    :copyright: (c) 2017 by Sean Callaway.
    :license: MIT, see LICENSE for more details.
"""
import requests
import json

def get_joke():
    """Returns a joke from the WebKnox one liner API.

    Returns None if unable to retrieve a joke.
    """

    headers = {'Accept' : 'application/json'}
    page = requests.get("https://icanhazdadjoke.com", headers=headers)

    if page.status_code == 200:
       joke = json.loads(page.content.decode("UTF-8"))
       return joke["joke"]

    return None
