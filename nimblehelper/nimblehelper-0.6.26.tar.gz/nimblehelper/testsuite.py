from requests import post, get
from .settings import KONG_ADMIN_URL


def login(url, username, password):
    data = {"username": username, "password": password}
    return post(url=url, data=data)


def get_x_consumer_id(username):
    url = KONG_ADMIN_URL + "consumers/" + username + "/"
    return get(url=url)
