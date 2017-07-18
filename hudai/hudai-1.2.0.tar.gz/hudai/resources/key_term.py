from hudai.resource import Resource
from pydash import pick


class KeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client)
        self.resource_name = 'KeyTerm'


    def associated_users(self, term):
        return self._associated_with(term, 'users')


    def associated_companies(self, term):
        return self._associated_with(term, 'companies')


    def associated_articles(self, term):
        return self._associated_with(term, 'articles')


    def list_for_user(self, user_id):
        return self._list_for('user_id', user_id)


    def list_for_company(self, company_id):
        return self._list_for('company_id', company_id)


    def list_for_article(self, article_id):
        return self._list_for('article_id', article_id)


    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'keyterm'),
            'url': '/key-terms/internal'
        })


    def get(self, id):
        return self.request({
            'method': 'GET',
            'params': {'id': id},
            'url': '/key-terms/internal/{id}'
        })


    def delete(self, id):
        return self.request({
            'method': 'DELETE',
            'params': {'id': id},
            'url': '/key-terms/internal/{id}'
        })


    def _associated_with(self, term, association):
        return self.request({
            'method': 'GET',
            'params': {'term': term, 'association': association},
            'url': '/key-terms/internal'
        })

    def _list_for(self, key, val):
        return self.request({
            'method': 'GET',
            'params': { key : val },
            'url': '/key-terms/internal'
        })
