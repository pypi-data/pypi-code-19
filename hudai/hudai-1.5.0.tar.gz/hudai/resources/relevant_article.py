from hudai.resource import Resource
from pydash import pick


class RelevantArticleResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/relevant-articles')
        self.resource_name = 'RelevantArticle'

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'user', 'scored_at'),
            'url': '/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'user', 'scored_at', 'relevant_articles'),
            'url': '/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'scored_at', 'relevant_articles'),
            'params': pick(params, 'user'),
            'url': '/internal/{user}'
        })

    def delete(self, user):
        return self.request({
            'method': 'DELETE',
            'params': {'user': user},
            'url': '/internal/{user}'
        })
