from ..resource import Resource


class SystemTaskResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/system-tasks')
        self.resource_name = 'SystemTask'

    def list(self,
             page=None,
             started_after=None,
             started_before=None,
             completed=None):
        return self._list(
            page=page,
            started_after=started_after,
            started_before=started_before,
            completed=completed
        )

    def create(self, entity_id=None, started_at=None, completed_at=None):
        return self._create(
            id=entity_id,
            started_at=started_at,
            completed_at=completed_at
        )

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id, started_at=None, completed_at=None):
        return self._update(entity_id,
            started_at=started_at,
            completed_at=completed_at
        )

    def delete(self, entity_id):
        return self._delete(entity_id)
