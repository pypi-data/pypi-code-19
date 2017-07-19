import requests

from hudai import __version__, HudAiError
from hudai.resources import *

USER_AGENT = 'HUD.ai Python v{} +(https://github.com/FoundryAI/hud-ai-python#readme)'.format(__version__)

class HudAi:
    def __init__(self, api_key=None, base_url='https://api.hud.ai'):
        if not api_key:
            raise HudAiError('missing api_key', 'initialization_error')

        self._api_key = api_key
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


    def get(self, path, params={}, data={}):
        return requests.get(self._build_url(path),
                            params=params,
                            data=data,
                            headers=self._get_headers())


    def post(self, path, params={}, data={}):
        return requests.post(self._build_url(path),
                            params=params,
                            data=data,
                            headers=self._get_headers())


    def put(self, path, params={}, data={}):
        return requests.put(self._build_url(path),
                            params=params,
                            data=data,
                            headers=self._get_headers())


    def patch(self, path, params={}, data={}):
        return requests.patch(self._build_url(path),
                            params=params,
                            data=data,
                            headers=self._get_headers())


    def delete(self, path, params={}, data={}):
        return requests.delete(self._build_url(path),
                            params=params,
                            data=data,
                            headers=self._get_headers())


    def _build_url(self, path):
        return '{}{}'.format(self._base_url, path)


    def _get_headers(self):
        return { 'User-Agent': USER_AGENT, 'x-api-key': self._api_key }
