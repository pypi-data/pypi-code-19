from ..resource import Resource


class TextCorpusResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/text-corpora')
        self.resource_name = 'TextCorpus'

    def list(self, user_id=None, type=None):
        return self._list(user_id=user_id, type=type)

    def create(self, user_id=None, type=None, body=None):
        return self._create(user_id=user_id, type=type, body=body)

    def get(self, id):
        return self._get(id)

    def update(self, id, user_id=None, type=None, body=None):
        return self._update(id, user_id=user_id, type=type, body=body)

    def delete(self, id):
        return self._delete(id)
