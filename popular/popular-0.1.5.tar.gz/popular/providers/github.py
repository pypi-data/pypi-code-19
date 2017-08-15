from gettext import gettext as _
import requests

from .base import Provider
from ..exceptions import SocialError, SocialProviderError
from ..users import User


class GithubProvider(Provider):
    """Provider for github.com authentication."""

    CONFIG_KEYS = [
        'client_id',
        'client_secret',
        'redirect_uri',
    ]

    def get_auth_url(self, state):
        """Generates the url for the user to grant permission on.

        Args:
            state: a string of random characters to help prevent CSRF
                attacks.

        Returns:
            A string URL.
        """
        url = 'http://github.com/login/oauth/authorize'
        return self.serialize_url(url=url, params=dict(
            client_id=self.config['client_id'],
            redirect_uri=self.config['redirect_uri'],
            scope=' '.join(['user:email']),
            state=state,
            allow_signup='true',
        ))

    def get_user(self, uri, state):
        """Takes the response URI and retrieves a user from it.

        Args:
            uri: a string uri that the service sent the user to,
                including all query paramters attached.
            state: a string that was provided for this exact request
                when the user was first redirected.

        Returns:
            A popular.users.User instance.

        Raises:
            The state parameter is invalid.
        """
        # See if the uri has what we expect.
        uri_params = self.parse_uri(uri, required=['code', 'state'])
        if uri_params['state'] != state:
            raise SocialError(_("The state parameter is invalid."))

        # Get the access token from the API.
        url = 'https://github.com/login/oauth/access_token'
        headers = {'Accept': 'application/json'}
        data = dict(
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret'],
            redirect_uri=self.config['redirect_uri'],
            code=uri_params['code'],
            state=state,
        )
        r = requests.post(url, headers=headers, data=data)
        access_token = self.response_to_dict(r)['access_token']

        # Grab the user from the API.
        url = 'https://api.github.com/user'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'token %s' % access_token,
        }
        r = requests.get(url, headers=headers)
        raw = self.response_to_dict(r)
        user = User()
        user.set_raw(raw)
        user.map(
            id=raw['id'],
            name=raw['name'],
            nickname=raw['login'],
            avatar=raw.get('avatar_url', None),
        )

        # Grab the email from the API.
        url = 'https://api.github.com/user/emails'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'token %s' % access_token,
        }
        r = requests.get(url, headers=headers)
        raw = self.response_to_dict(r)
        for email in raw:
            user.map(email=email['email'])
            if email['primary'] == True:
                break
        return user

    def response_to_dict(self, response):
        """Helper to gracefully return error messages from API."""
        output = response.json()
        if response.status_code != 200:
            raise SocialProviderError(output['message'])
        if 'error' in output:
            raise SocialProviderError(output['error'])
        return output


# Make a consistent reference for the Manager to use.
provider = GithubProvider
