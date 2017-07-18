from hudai.resource import Resource
from pydash import pick


class ArticleCompanyResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client)
        self.resource_name = 'ArticleCompany'

    def get(self, article_uuid):
        return self.request({
            'method': 'GET',
            'params': {'article_uuid': article_uuid},
            'url': '/article-companies/internal/{article_uuid}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'company_id', 'article_type', 'published_at'),
            'url': '/article-companies/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'company_id', 'article_type', 'published_at'),
            'url': '/article-companies/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'company'),
            'params': pick(params, 'article_uuid'),
            'url': '/article-companies/internal/{article_uuid}'
        })

    def delete(self, article_uuid):
        return self.request({
            'method': 'DELETE',
            'params': {'id': article_uuid},
            'url': '/article-companies/internal/{article_uuid}'
        })
