import requests

from fs_cli.config import MANAGEMENT_URL
from requests.auth import HTTPBasicAuth


def create_app(auth, params):
    return requests.post("{}/apps".format(MANAGEMENT_URL), json=params, auth=HTTPBasicAuth(*auth))

def list_apps(auth, params=None):
    return requests.get("{}/apps".format(MANAGEMENT_URL), params=params, auth=HTTPBasicAuth(*auth))
