"""HUD.ai Client Specs

Ensure that the client continues to act in a predictable way so that it can be
extended via the Resources or used directly to perform the required translations
and inject any required headers
"""

from datetime import datetime
import pytest
import requests

from hudai.client import HudAi
from hudai.resources import *


def test_initialization():
    client = HudAi(api_key='mock-api-key')

    assert isinstance(client, HudAi)
    assert isinstance(client.article_highlights, ArticleHighlightsResource)
    assert isinstance(client.article_key_term, ArticleKeyTermResource)
    assert isinstance(client.article, ArticleResource)
    assert isinstance(client.company_key_term, CompanyKeyTermResource)
    assert isinstance(client.company, CompanyResource)
    assert isinstance(client.domain, DomainResource)
    assert isinstance(client.key_term, KeyTermResource)
    assert isinstance(client.system_event, SystemEventResource)
    assert isinstance(client.system_task, SystemTaskResource)
    assert isinstance(client.text_corpus, TextCorpusResource)
    assert isinstance(client.user_company, UserCompanyResource)
    assert isinstance(client.user_key_term, UserKeyTermResource)
    assert isinstance(client.user, UserResource)


@pytest.mark.parametrize('http_verb', [('get'), ('post'), ('put'), ('patch'), ('delete')])
def test_required_parameter_injection(mocker, http_verb):
    client = HudAi(api_key='mock-api-key')
    mocker.patch.object(requests, http_verb)

    # Actual function call, e.g. client.get(path, params)
    function_under_test = getattr(client, "http_{}".format(http_verb))
    requests_function = getattr(requests, http_verb)

    assert callable(function_under_test)

    function_under_test('/test/url')

    assert requests_function.call_count == 1

    args, kwargs = requests_function.call_args

    assert args[0] == 'https://api.hud.ai/v1/test/url'
    assert kwargs['headers']['x-api-key'] == 'mock-api-key'


@pytest.mark.parametrize('http_verb', [('get'), ('delete')])
def test_passing_requests_params(mocker, http_verb):
    client = HudAi(api_key='mock-api-key')
    mocker.patch.object(requests, http_verb)

    # Actual function call, e.g. client.get(path, params)
    function_under_test = getattr(client, "http_{}".format(http_verb))
    requests_function = getattr(requests, http_verb)

    function_under_test('/test/url', query_params={'foo_bar':'baz'})

    _, kwargs = requests_function.call_args

    assert kwargs['params'] == {'foo_bar':'baz'}


@pytest.mark.parametrize('http_verb', [('post'), ('put'), ('patch')])
def test_passing_requests_params_with_data(mocker, http_verb):
    client = HudAi(api_key='mock-api-key')
    mocker.patch.object(requests, http_verb)

    # Actual function call, e.g. client.get(path, params)
    function_under_test = getattr(client, "http_{}".format(http_verb))
    requests_function = getattr(requests, http_verb)

    function_under_test('/test/url',
                        query_params={'foo_bar':'baz'},
                        data={'fizz_buzz':{'abc':'jackson_five'}})

    _, kwargs = requests_function.call_args

    assert kwargs['params'] == {'foo_bar':'baz'}
    assert kwargs['data'] == {'fizzBuzz':{'abc':'jackson_five'}}


def test_jsonifiying(mocker):
    client = HudAi(api_key='mock-api-key')
    mocker.patch('requests.post')

    timestamp = datetime.now()
    formatted_timestamp = timestamp.isoformat()

    client.http_post('/test/url',
                     query_params={'abc':timestamp},
                     data={'xyz':timestamp})

    _, kwargs = requests.post.call_args

    assert kwargs['params']['abc'] == formatted_timestamp
    assert kwargs['data']['xyz'] == formatted_timestamp


def test_pythonification(mocker):
    client = HudAi(api_key='mock-api-key')

    mock_json = {
        'string': 'test-string',
        'boolean': True,
        'number': 123,
        'date': '2017-07-28T15:30:08.176077',
        'array': ['test', '2017-07-28T15:30:08.176077', 123],
        'object': {
            'nestedString': 'test2',
            'nestedDate': '2017-07-28T15:30:08.176077'
        }
    }

    mock_response = requests.Response()
    mocker.patch('requests.get').return_value = mock_response
    mocker.patch.object(mock_response, 'json').return_value = mock_json

    expected_timestamp = datetime(2017, 7, 28, 15, 30, 8, 176077)

    response = client.http_get('/test/url')

    assert response['string'] == 'test-string'
    assert response['boolean']
    assert response['number'] == 123
    assert response['date'] == expected_timestamp
    assert response['array'] == ['test', expected_timestamp, 123]
    assert response['object']['nested_string'] == 'test2'
    assert response['object']['nested_date'] == expected_timestamp
