from hudai.resource import Resource
from pydash import pick


class CleanArticleResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/clean-articles')
        self.resource_name = 'CleanArticle'

    def get(self, uuid):
        return self.request({
            'method': 'GET',
            'params': {'uuid': uuid},
            'url': '/internal/{uuid}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'query': pick(params, 'uuid', 'article_type', 'description', 'important_score', 'link', 'source', 'title', 'published_at'),
            'url': '/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'article_type', 'description', 'important_score', 'link', 'source', 'title', 'published_at'),
            'url': '/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'article_type', 'description', 'important_score', 'link', 'source', 'title', 'published_at'),
            'params': pick(params, 'uuid'),
            'url': '/internal/{uuid}'
        })

    def delete(self, uuid):
        return self.request({
            'method': 'DELETE',
            'params': {'uuid': uuid},
            'url': '/internal/{uuid}'
        })
