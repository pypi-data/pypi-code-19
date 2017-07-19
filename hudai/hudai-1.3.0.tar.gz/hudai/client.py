from requests import Request, Session

from hudai import __version__, HudAiError
from hudai.resources import *

USER_AGENT = 'HUD.ai Python v{} +(https://github.com/FoundryAI/hud-ai-python#readme)'.format(__version__)

class HudAi:
    def __init__(self, secret_key, base_url='https://api.hud.ai'):
        if not secret_key:
            raise HudAiError('missing secret_key', 'initialization_error')

        self._secret_key = secret_key
        self._base_url = base_url

        self.article_company = ArticleCompanyResource(self)
        self.article_highlights = ArticleHighlightsResource(self)
        self.article_key_term = ArticleKeyTermResource(self)
        self.clean_article = CleanArticleResource(self)
        self.company = CompanyResource(self)
        self.domain = DomainResource(self)
        self.key_term = KeyTermResource(self)
        self.message = MessageResource(self)
        self.news_api_article = NewsApiArticleResource(self)
        self.participant = ParticipantResource(self)
        self.relevant_article = RelevantArticleResource(self)
        self.rss_article = RssArticleResource(self)
        self.rss_feed_metadata = RssFeedMetadataResource(self)
        self.task = TaskResource(self)
        self.text_corpus = TextCorpusResource(self)
        self.user = UserResource(self)

    def make_request(self, method, path, params, data):
        """
        Abstracted request method, request config is defined in the resource itself
        :param method:
        :param path:
        :param params:
        :param data:
        :return:
        """
        session = Session()
        req = Request(method, (self._base_url + path), data=data, params=params)
        prepared = req.prepare()
        prepared.headers['User-Agent'] = USER_AGENT
        prepared.headers['x-api-key'] = self._secret_key
        return session.send(prepared).json()
