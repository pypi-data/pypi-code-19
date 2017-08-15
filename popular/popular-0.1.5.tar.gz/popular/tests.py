import pytest

from .exceptions import SocialError
from . import Popular as Manager


def test_manager_empty_success():
    Manager({})

def test_manager_github_success():
    Manager({
        'github': {
            'client_id': 'moose',
            'client_secret': 'moose',
            'redirect_uri': 'moose',
        },
    })

def test_manager_github_failure():
    with pytest.raises(SocialError) as err:
        Manager({
            'github': {
                'client_id': 'moose',
                'client_secret': 'moose',
                '0redirect_uri': 'moose',
            },
        })
    assert str(err.value).startswith(
        'The github provider requires the following keys: '
    )

def test_manager_type_failure():
    with pytest.raises(ValueError) as err:
        Manager('moose')
    assert str(err.value) == "The popular configuration must be a dict."

def test_manager_nonexistant_failure():
    with pytest.raises(SocialError) as err:
        Manager({'base': {}})
    assert str(err.value) == 'The popular provider base does not exist.'
    with pytest.raises(SocialError) as err:
        Manager({'moose': {}})
    assert str(err.value) == 'The popular provider moose does not exist.'
