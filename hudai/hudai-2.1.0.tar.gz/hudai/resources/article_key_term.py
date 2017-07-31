from ..resource import Resource


class ArticleKeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/article-key-terms')
        self.resource_name = 'ArticleKeyTerm'

    def list(self, term=None, article_id=None):
        return self._list(term=term, article_id=article_id)

    def create(self, term=None, article_id=None):
        return self._create(term=term, article_id=article_id)

    def get(self, id):
        return self._get(id)

    def delete(self, id):
        return self._delete(id)
