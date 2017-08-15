import pytest


from .facebook import FacebookProvider
from .github import GithubProvider
from .google import GoogleProvider


def test_facebook_provider_auth_url_success():
    provider = FacebookProvider({
        'client_id': 'moose',
        'client_secret': 'moose',
        'redirect_uri': 'https://moose.com/callback',
    })
    url = provider.get_auth_url(state='moose')


def test_github_provider_auth_url_success():
    provider = GithubProvider({
        'client_id': 'moose',
        'client_secret': 'moose',
        'redirect_uri': 'https://moose.com/callback',
    })
    url = provider.get_auth_url(state='moose')


def test_google_provider_auth_url_success():
    provider = GoogleProvider({
        'client_id': 'moose',
        'client_secret': 'moose',
        'redirect_uri': 'https://moose.com/callback',
    })
    url = provider.get_auth_url(state='moose')
