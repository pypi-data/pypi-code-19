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


@pytest.mark.parametrize('http_verb', [('get'),('post'),('put'),('patch'),('delete')])
def test_required_parameter_injection(mocker, http_verb):
    client = HudAi(api_key='mock-api-key')
    mocker.patch.object(requests, http_verb, autospec=True)

    # Actual function call, e.g. client.get(path, params)
    function_under_test = getattr(client, http_verb)
    requests_function = getattr(requests, http_verb)

    assert callable(function_under_test)

    function_under_test('/test/url')

    assert requests_function.call_count == 1

    args, kwargs = requests_function.call_args

    assert args[0] == 'https://api.hud.ai/v1/test/url'
    assert kwargs['headers']['x-api-key'] == 'mock-api-key'


@pytest.mark.parametrize('http_verb', [('get'),('post'),('put'),('patch'),('delete')])
def test_passing_parameters(mocker, http_verb):
    client = HudAi(api_key='mock-api-key')
    mocker.patch.object(requests, http_verb, autospec=True)

    # Actual function call, e.g. client.get(path, params)
    function_under_test = getattr(client, http_verb)
    requests_function = getattr(requests, http_verb)

    function_under_test('/test/url',
                        query_params={'foo_bar':'baz'},
                        data={'fizz_buzz':{'abc':'jackson_five'}})

    args, kwargs = requests_function.call_args

    assert kwargs['params'] == {'foo_bar':'baz'}
    assert kwargs['data'] == {'fizzBuzz':{'abc':'jackson_five'}}
