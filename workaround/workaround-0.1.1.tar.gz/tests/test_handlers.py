import pytest
import regex
import responses
from requests import HTTPError

from workaround.handlers import (
    get_all_adjectives,
    get_handler,
    get_handlers,
)
from workaround.handlers.django import (
    DjangoHandler,
    get_ticket_state,
)
from workaround.handlers.github import GithubHandler
from workaround.handlers.npm import NPMHandler
from workaround.handlers.pypi import PyPiHandler

from .conftest import BUILTIN_HANDLERS


class TestGetFunctions:
    def test_get_handlers_contains_all_items(self):
        assert set(get_handlers().values()) == set(BUILTIN_HANDLERS)

    def test_get_all_adjectives(self):
        adjectives = get_all_adjectives()
        assert adjectives
        assert isinstance(adjectives, set)

    def test_get_handler(self, handler_class):
        for value, adjective in handler_class.examples():
            assert isinstance(get_handler(value, adjective), handler_class)


class TestHandlerAttributes:
    def test_has_examples(self, handler):
        assert handler.example_values

    def test_parse_example_values(self, handler):
        for value in handler.example_values:
            assert handler.extract_info_from_value(value)

    def test_has_adjectives(self, handler):
        assert handler.adjectives

    def test_value_patterns(self, handler):
        assert handler.value_patterns

        for pattern in handler.value_patterns:
            regex.compile(pattern)


class TestGithubHandler:
    @pytest.mark.parametrize('given,adjective,expected', [
        ({'merged': True}, 'merged', True),
        ({'merged': False}, 'merged', False),
        ({'merged': True, 'state': 'closed'}, 'closed', True),
        ({'merged': True, 'state': 'open'}, 'closed', False),
        ({'merged': True, 'state': 'open'}, 'open', True),
        ({'merged': True, 'state': 'closed'}, 'open', False),
    ])
    def test_is_result_equal(self, given, adjective, expected):
        handler = GithubHandler()
        assert handler.is_result_equal(given, adjective) == expected

    @responses.activate
    def test_get_result_issue(self, workaround):
        handler = GithubHandler()
        REPO_ATTRS = {'user': 'orf', 'repo': 'orf', 'type': 'issue', 'id': '12'}
        responses.add(responses.GET, handler.GITHUB_URL.format(**REPO_ATTRS),
                      json={'state': 'open'})
        assert handler.get_result(workaround, REPO_ATTRS) == {'state': 'open', 'merged': None}

    @responses.activate
    def test_get_result_merge_request(self, workaround):
        handler = GithubHandler()
        REPO_ATTRS = {'user': 'orf', 'repo': 'orf', 'type': 'pulls', 'id': '12'}
        responses.add(responses.GET, handler.GITHUB_URL.format(**REPO_ATTRS),
                      json={'state': 'closed', 'merged': True})
        assert handler.get_result(workaround, REPO_ATTRS) == {'state': 'closed', 'merged': True}

    GITHUB = 'https://github.com/'

    @pytest.mark.parametrize('value,expected', [
        (GITHUB + 'django/django', None),
        (GITHUB + 'django/django/pull/123', {'repo': 'django', 'user': 'django', 'type': 'pulls', 'id': '123'}),
        (GITHUB + 'django/django/pulls/123', {'repo': 'django', 'user': 'django', 'type': 'pulls', 'id': '123'}),
        (GITHUB + 'django/django/issue/123', {'repo': 'django', 'user': 'django', 'type': 'issues', 'id': '123'}),
        (GITHUB + 'django/django/issues/123', {'repo': 'django', 'user': 'django', 'type': 'issues', 'id': '123'}),
        (GITHUB + 'django/djangoproject.com/issues/123', {'repo': 'djangoproject.com', 'user': 'django',
                                                          'type': 'issues', 'id': '123'}),
    ])
    def test_extract_info(self, value, expected):
        handler = GithubHandler()
        assert handler.extract_info_from_value(value) == expected


class TestNPMHandler:
    RELEASE_RESPONSE = {'versions': {'0.1.0': None, '0.2.0': None, '0.3.0': None}}

    @responses.activate
    def test_get_result_released_package(self, workaround):
        handler = NPMHandler()
        responses.add(responses.GET, handler.NPM_URL.format(package='test'),
                      json=self.RELEASE_RESPONSE)
        assert handler.get_result(workaround, {'spec': '>0.2.0', 'package': 'test'}) == 'released'

    @responses.activate
    def test_get_result_unreleased_package(self, workaround):
        handler = NPMHandler()
        responses.add(responses.GET, handler.NPM_URL.format(package='test'),
                      json=self.RELEASE_RESPONSE)
        assert handler.get_result(workaround, {'spec': '>0.3.0', 'package': 'test'}) == 'unreleased'

    @pytest.mark.parametrize('value,expected', [
        ('not-npm:abc def', None),
        ('npm:babel', None),
        ('npm:babel ~1.0.0', {'package': 'babel', 'spec': '~1.0.0'}),
        ('npm:babel <1.0.0', {'package': 'babel', 'spec': '<1.0.0'})
    ])
    def test_extract_info(self, value, expected):
        handler = NPMHandler()
        assert handler.extract_info_from_value(value) == expected

    @pytest.mark.parametrize('given,adjective,expected', [
        ('released', 'released', True),
        ('released', 'unreleased', False)
    ])
    def test_is_result_equal(self, given, adjective, expected):
        handler = NPMHandler()
        assert handler.is_result_equal(given, adjective) == expected


class TestPyPiHandler:
    RELEASE_RESPONSE = {'releases': {'0.1': None, '0.2': None, '0.3': None}}

    @responses.activate
    def test_get_result_released_package(self, workaround):
        handler = PyPiHandler()
        responses.add(responses.GET, handler.PYPI_URL.format(package='test'),
                      json=self.RELEASE_RESPONSE)
        assert handler.get_result(workaround, {'value': 'test>0.2'}) == 'released'

    @responses.activate
    def test_get_result_unreleased_package(self, workaround):
        handler = PyPiHandler()
        responses.add(responses.GET, handler.PYPI_URL.format(package='test'),
                      json=self.RELEASE_RESPONSE)
        assert handler.get_result(workaround, {'value': 'test>0.3'}) == 'unreleased'

    @responses.activate
    def test_get_result_no_version(self, workaround):
        handler = PyPiHandler()
        responses.add(responses.GET, handler.PYPI_URL.format(package='test'),
                      json=self.RELEASE_RESPONSE)
        assert handler.get_result(workaround, {'value': 'test'}) == 'released'

    @pytest.mark.parametrize('value,expected', [
        ('pypi:babel', {'value': 'babel'}),
        ('pypi:babel~=1.0', {'value': 'babel~=1.0'}),
        ('pypi:babel<=2', {'value': 'babel<=2'}),
    ])
    def test_extract_info(self, value, expected):
        handler = PyPiHandler()
        assert handler.extract_info_from_value(value) == expected

    @pytest.mark.parametrize('given,adjective,expected', [
        ('released', 'released', True),
        ('released', 'unreleased', False)
    ])
    def test_is_result_equal(self, given, adjective, expected):
        handler = PyPiHandler()
        assert handler.is_result_equal(given, adjective) == expected


class TestDjangoHandler:
    @responses.activate
    def test_get_ticket_state_throws(self):
        responses.add(responses.GET, 'https://code.djangoproject.com/jsonrpc',
                      status=500)
        with pytest.raises(HTTPError):
            get_ticket_state('123')

    @responses.activate
    def test_get_ticket_state_returns_values(self):
        json = {'result': [
            123,
            {},
            {},
            {'resolution': 'foo', 'status': 'bar'}
        ]}
        responses.add(responses.GET, 'https://code.djangoproject.com/jsonrpc',
                      json=json)
        result = get_ticket_state('123')
        assert result == ('foo', 'bar')

    @responses.activate
    def test_get_result_state_returns_values(self, workaround):
        json = {'result': [
            123,
            {},
            {},
            {'resolution': 'foo', 'status': 'bar'}
        ]}
        responses.add(responses.GET, 'https://code.djangoproject.com/jsonrpc',
                      json=json)
        handler = DjangoHandler()
        result = handler.get_result(workaround, {'ticket_id': '123'})
        assert result == ('foo', 'bar')

    @pytest.mark.parametrize('result,adjective,expected', [
        (('fixed', 'closed'), 'fixed', True),
        (('fixed', 'closed'), 'open', False),
        (('fixed', 'closed'), 'abc', False),
        (('not-fixed', 'open'), 'open', True),
    ])
    def test_is_result_equal(self, result, adjective, expected):
        handler = DjangoHandler()
        assert handler.is_result_equal(result, adjective) == expected

    @pytest.mark.parametrize('value,expected', [
        ('django:123', {'ticket_id': '123'}),
        ('django:hello', None),
        ('https://code.djangoproject.com/ticket/278/', {'ticket_id': '278'}),
        ('https://code.djangoproject.com/', None)
    ])
    def test_extract_info(self, value, expected):
        handler = DjangoHandler()
        assert handler.extract_info_from_value(value) == expected
