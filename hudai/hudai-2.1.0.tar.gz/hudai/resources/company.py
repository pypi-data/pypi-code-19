from ..resource import Resource


class CompanyResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/companies')
        self.resource_name = 'Company'

    def list(self):
        return self._list()

    def create(self, name=None):
        return self._create(name=name)

    def get(self, id):
        return self._get(id)

    def update(self, id, name=None):
        return self._update(id, name=name)

    def delete(self, id):
        return self._delete(id)

    def domains(self, id):
        return self.get('/{id}/domains', {
            'params': {'id': id}
        })

    def key_terms(self, id):
        return self.get('/{id}/key-terms', {
            'params': {'id': id}
        })
