import requests

from yo_client.urls import SEND_YO_URL, SEND_YOS_TO_ALL_SUBSCRIBERS_URL, CREATE_ACCOUNT_URL, USERNAME_EXISTS_URL, \
    SUBSCRIBERS_COUNT_URL
from yo_client.request_parameters import RequestBodyBuilder, RequestQueryParametersBuilder


class YoClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def send_yo(self, username, text=None, link=None, coordinate=None):
        r = requests.post(url=SEND_YO_URL,
                          data=RequestBodyBuilder.build_send_yo_body(username=username, api_token=self.api_key,
                                                                     text=text, link=link, coordinate=coordinate))

        r.raise_for_status()

        return r.json()

    def send_yo_to_all_subscribers(self, link=None):
        r = requests.post(url=SEND_YOS_TO_ALL_SUBSCRIBERS_URL,
                          data=RequestBodyBuilder.build_send_yo_to_all_subscribers_body(api_token=self.api_key, link=link))

        r.raise_for_status()

        return r.json()

    def create_account(self, username, password=None, callback_url=None, email=None, description=None, needs_location=False, welcome_link=None):
        r = requests.post(url=CREATE_ACCOUNT_URL, data=RequestBodyBuilder.build_account_creation_body(username=username, api_token=self.api_key, password=password, callback_url=callback_url, email=email, description=description, needs_location=needs_location, welcome_link=welcome_link))

        r.raise_for_status()

        return r.json()

    def username_exists(self, username):
        r = requests.get(url=USERNAME_EXISTS_URL, data=RequestQueryParametersBuilder.build_username_exists_query_parameters(username=username, api_token=self.api_key))

        r.raise_for_status()

        return r.json()

    def get_subscribers_count(self):
        r = requests.get(url=SUBSCRIBERS_COUNT_URL, data={"api_token": self.api_key})

        r.raise_for_status()

        return r.json()
