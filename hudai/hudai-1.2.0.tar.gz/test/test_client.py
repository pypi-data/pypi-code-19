from hudai.client import HudAi
from hudai.resources import *


def test_initialization():
    client = HudAi('mock-api-key')

    assert isinstance(client, HudAi)
    assert isinstance(client.article_company, ArticleCompanyResource)
    assert isinstance(client.article_highlight, ArticleHighlightResource)
    assert isinstance(client.article_keyterm, ArticleKeytermResource)
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
