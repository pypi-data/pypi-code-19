from hudai.resource import Resource
from pydash import pick


class ArticleKeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/article-key-terms')
        self.resource_name = 'ArticleKeyTerm'

    def list(self, params):
        return self.request({
            'params': pick(params, 'term', 'published_before', 'published_after'),
            'url': '/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'article_id', 'term', 'published_at'),
            'url': '/internal'
        })

    def delete(self, article_id, term):
        return self.request({
            'method': 'DELETE',
            'params': { 'article_id' : article_id, 'term' : term },
            'url': '/internal/{article_id}/{term}'
        })
