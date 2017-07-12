from hudai.error import HudAiError
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

class HudAiClient:
    @staticmethod
    def create(secret_key):
        return HudAiClient(secret_key)

    def __init__(self, secret_key):
        self.secret_key = secret_key

        if self.secret_key is None:
            raise HudAiError('Missing required "secretKey".', 'authentication_error')

        self.article_company = ArticleCompanyResource(secret_key)
        self.article_keyterm = ArticleKeytermResource(secret_key)
        self.clean_article = CleanArticleResource(secret_key)
        self.company = CompanyResource(secret_key)
        self.domain = DomainResource(secret_key)
        self.message = MessageResource(secret_key)
        self.news_api_article = NewsApiArticleResource(secret_key)
        self.participant = ParticipantResource(secret_key)
        self.relevant_article = RelevantArticleResource(secret_key)
        self.rss_article = RssArticleResource(secret_key)
        self.rss_feed_metadata = RssFeedMetadataResource(secret_key)
        self.task = TaskResource(secret_key)
        self.text_corpus = TextCorpusResource(secret_key)
        self.user = UserResource(secret_key)
