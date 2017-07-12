from hudai.resource import Resource
from pydash import pick


class CleanArticleResource(Resource):
    def __init__(self, secret_key):
        Resource.__init__(self, secret_key)
        self.resource_name = 'CleanArticle'

    def get(self, uuid):
        return self.make_request({
            'method': 'GET',
            'params': {'uuid': uuid},
            'url': '/clean-articles/internal/{uuid}'
        })

    def search(self, params):
        return self.make_request({
            'method': 'GET',
            'params': pick(params, 'article_type', 'description', 'important_score', 'link', 'source', 'title', 'published_at'),
            'url': '/clean-articles/internal'
        })

    def create(self, params):
        return self.make_request({
            'method': 'POST',
            'data': pick(params, 'article_type', 'description', 'important_score', 'link', 'source', 'title', 'published_at'),
            'url': '/clean-articles/internal'
        })

    def update(self, params):
        return self.make_request({
            'method': 'PUT',
            'data': pick(params, 'article_type', 'description', 'important_score', 'link', 'source', 'title', 'published_at'),
            'params': pick(params, 'uuid'),
            'url': '/clean-articles/internal/{uuid}'
        })

    def delete(self, uuid):
        return self.make_request({
            'method': 'DELETE',
            'params': {'uuid': uuid},
            'url': '/clean-articles/internal/{uuid}'
        })
