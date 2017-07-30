import pathlib

import pytest
import regex

from workaround import Workaround
from workaround.handlers.django import DjangoHandler
from workaround.handlers.github import GithubHandler
from workaround.handlers.npm import NPMHandler
from workaround.handlers.pypi import PyPiHandler

BUILTIN_HANDLERS = [DjangoHandler, GithubHandler, NPMHandler, PyPiHandler]


@pytest.fixture(params=BUILTIN_HANDLERS)
def handler_class(request):
    return request.param


@pytest.fixture(params=BUILTIN_HANDLERS)
def handler(request):
    return request.param()


@pytest.fixture()
def regex_match():
    return regex.match('(?P<statement>(?P<adjective>.*) (?P<value>.*))', 'one two three')


@pytest.fixture()
def workaround(regex_match):
    return Workaround(
        match=regex_match,
        path=pathlib.Path(__file__),
        context=(
            'first line\nsecond line\n',
            'fourth line\nfifth line\n'
        ),
        line=regex_match.string
    )
