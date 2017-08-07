import requests

import russell
from russell.exceptions import AuthenticationException
from russell.client.base import RussellHttpClient
from russell.model.user import User

class AuthClient(RussellHttpClient):
    """
    Auth/User specific client
    """
    def __init__(self):
        self.base_url = "{}/api/v1/user/".format(russell.russell_host)

    def get_user(self, access_token):
        response = requests.get(self.base_url,
                                headers={"Authorization": "Basic {}".format(access_token)})
        try:
            user_dict = response.json()
        except Exception:
            raise AuthenticationException("Invalid Token")
        return User.from_dict(user_dict)
