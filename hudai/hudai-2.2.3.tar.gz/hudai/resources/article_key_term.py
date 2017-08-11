"""
hudai.resources.article_key_term
"""
from ..resource import Resource


class ArticleKeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/article-key-terms')
        self.resource_name = 'ArticleKeyTerm'

    def list(self, term=None, article_id=None):
        return self._list(term=term, article_id=article_id)

    def create(self, term=None, article_id=None):
        return self._create(term=term, article_id=article_id)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def delete(self, entity_id):
        return self._delete(entity_id)
