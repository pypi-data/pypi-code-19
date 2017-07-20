import requests

from hudai.client import HudAi
from hudai.resources import *


TEST_PATH = '/test/url'
TEST_PARAMS = {'foo':'bar'}
TEST_DATA = {'fizz':'buzz'}


def test_initialization():
    client = HudAi(api_key='mock-api-key')

    assert isinstance(client, HudAi)
    assert isinstance(client.article_company, ArticleCompanyResource)
    assert isinstance(client.article_highlights, ArticleHighlightsResource)
    assert isinstance(client.article_key_term, ArticleKeyTermResource)
    assert isinstance(client.clean_article, CleanArticleResource)
    assert isinstance(client.company, CompanyResource)
    assert isinstance(client.domain, DomainResource)
    assert isinstance(client.message, MessageResource)
    assert isinstance(client.news_api_article, NewsApiArticleResource)
    assert isinstance(client.participant, ParticipantResource)
    assert isinstance(client.relevant_article, RelevantArticleResource)
    assert isinstance(client.rss_article, RssArticleResource)
    assert isinstance(client.rss_feed_metadata, RssFeedMetadataResource)
    assert isinstance(client.task, TaskResource)
    assert isinstance(client.text_corpus, TextCorpusResource)
    assert isinstance(client.user, UserResource)


def test_get(mocker):
    client = HudAi(api_key='mock-api-key')
    mocker.patch('requests.get')

    assert callable(client.get)

    client.get(TEST_PATH, params=TEST_PARAMS, data=TEST_DATA)

    assert requests.get.call_count == 1

    args, kwargs = requests.get.call_args

    assert args[0] == 'https://api.hud.ai{}'.format(TEST_PATH)
    assert kwargs['params'] == TEST_PARAMS
    assert kwargs['data'] == TEST_DATA
    assert kwargs['headers']['x-api-key'] == 'mock-api-key'


def test_post(mocker):
    client = HudAi(api_key='mock-api-key')
    mocker.patch('requests.post')

    assert callable(client.post)

    client.post(TEST_PATH, params=TEST_PARAMS, data=TEST_DATA)

    assert requests.post.call_count == 1

    args, kwargs = requests.post.call_args

    assert args[0] == 'https://api.hud.ai{}'.format(TEST_PATH)
    assert kwargs['params'] == TEST_PARAMS
    assert kwargs['data'] == TEST_DATA
    assert kwargs['headers']['x-api-key'] == 'mock-api-key'


def test_put(mocker):
    client = HudAi(api_key='mock-api-key')
    mocker.patch('requests.put')

    assert callable(client.put)

    client.put(TEST_PATH, params=TEST_PARAMS, data=TEST_DATA)

    assert requests.put.call_count == 1

    args, kwargs = requests.put.call_args

    assert args[0] == 'https://api.hud.ai{}'.format(TEST_PATH)
    assert kwargs['params'] == TEST_PARAMS
    assert kwargs['data'] == TEST_DATA
    assert kwargs['headers']['x-api-key'] == 'mock-api-key'


def test_patch(mocker):
    client = HudAi(api_key='mock-api-key')
    mocker.patch('requests.patch')

    assert callable(client.patch)

    client.patch(TEST_PATH, params=TEST_PARAMS, data=TEST_DATA)

    assert requests.patch.call_count == 1

    args, kwargs = requests.patch.call_args

    assert args[0] == 'https://api.hud.ai{}'.format(TEST_PATH)
    assert kwargs['params'] == TEST_PARAMS
    assert kwargs['data'] == TEST_DATA
    assert kwargs['headers']['x-api-key'] == 'mock-api-key'


def test_delete(mocker):
    client = HudAi(api_key='mock-api-key')
    mocker.patch('requests.delete')

    assert callable(client.delete)

    client.delete(TEST_PATH, params=TEST_PARAMS, data=TEST_DATA)

    assert requests.delete.call_count == 1

    args, kwargs = requests.delete.call_args

    assert args[0] == 'https://api.hud.ai{}'.format(TEST_PATH)
    assert kwargs['params'] == TEST_PARAMS
    assert kwargs['data'] == TEST_DATA
    assert kwargs['headers']['x-api-key'] == 'mock-api-key'
