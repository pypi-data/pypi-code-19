from mock import patch
from unittest import TestCase
from mock import patch, MagicMock

from test.helpers.test_util import TestUtil
from hudai.hudai_client import HudAiClient

from hudai.resources.article_company import ArticleCompanyResource
from hudai.resources.article_keyterm import ArticleKeytermResource
from hudai.resources.clean_article import CleanArticleResource
from hudai.resources.company import CompanyResource
from hudai.resources.domain import DomainResource
from hudai.resources.message import MessageResource
from hudai.resources.news_api_article import NewsApiArticleResource
from hudai.resources.participant import ParticipantResource
from hudai.resources.relevant_article import RelevantArticleResource
from hudai.resources.rss_article import RssArticleResource
from hudai.resources.rss_feed_metadata import RssFeedMetadataResource
from hudai.resources.task import TaskResource
from hudai.resources.text_corpus import TextCorpusResource
from hudai.resources.user import UserResource


class TestHudAiClient(TestCase):
    def test_client(self):
        client = HudAiClient(TestUtil.get_key())
        self.assertIsInstance(client, HudAiClient)
        self.assertIsInstance(client.article_company, ArticleCompanyResource)
        self.assertIsInstance(client.article_keyterm, ArticleKeytermResource)
        self.assertIsInstance(client.clean_article, CleanArticleResource)
        self.assertIsInstance(client.company, CompanyResource)
        self.assertIsInstance(client.domain, DomainResource)
        self.assertIsInstance(client.message, MessageResource)
        self.assertIsInstance(client.news_api_article, NewsApiArticleResource)
        self.assertIsInstance(client.participant, ParticipantResource)
        self.assertIsInstance(client.relevant_article, RelevantArticleResource)
        self.assertIsInstance(client.rss_article, RssArticleResource)
        self.assertIsInstance(client.rss_feed_metadata, RssFeedMetadataResource)
        self.assertIsInstance(client.task, TaskResource)
        self.assertIsInstance(client.text_corpus, TextCorpusResource)
        self.assertIsInstance(client.user, UserResource)

    def test_client_static(self):
        self.assertTrue(HudAiClient.create)
        client = HudAiClient.create(TestUtil.get_key())
        self.assertIsInstance(client, HudAiClient)
        self.assertIsInstance(client.article_company, ArticleCompanyResource)
        self.assertIsInstance(client.article_keyterm, ArticleKeytermResource)
        self.assertIsInstance(client.clean_article, CleanArticleResource)
        self.assertIsInstance(client.company, CompanyResource)
        self.assertIsInstance(client.domain, DomainResource)
        self.assertIsInstance(client.message, MessageResource)
        self.assertIsInstance(client.news_api_article, NewsApiArticleResource)
        self.assertIsInstance(client.participant, ParticipantResource)
        self.assertIsInstance(client.relevant_article, RelevantArticleResource)
        self.assertIsInstance(client.rss_article, RssArticleResource)
        self.assertIsInstance(client.rss_feed_metadata, RssFeedMetadataResource)
        self.assertIsInstance(client.task, TaskResource)
        self.assertIsInstance(client.text_corpus, TextCorpusResource)
        self.assertIsInstance(client.user, UserResource)