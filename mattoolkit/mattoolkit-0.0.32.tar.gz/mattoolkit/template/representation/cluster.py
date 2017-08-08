from .base import BaseRepresentation
from ..schema import ClusterSchema
from ...api import ClusterResourceList, ClusterResourceItem

class ClusterRepresentation(BaseRepresentation):
    """ Cluster Representation

    """

    SCHEMA = ClusterSchema
    RESOURCE = ClusterResourceItem

    def _search_api_for_duplicates(self):
        duplicates = []
        clusters = ClusterResourceList()
        clusters.get()
        for cluster in clusters.items:
            if cluster.uri == self.uri:
                duplicates.append(cluster)
        return [item.id for item in duplicates]

    def as_api_resources(self):
        cluster_item = ClusterResourceItem(None)
        spec = self.document['spec']
        cluster_item.data = {
            'username': spec['ssh']['username'],
            'hostname': spec['ssh']['hostname'],
            'port': spec['ssh']['port'],
            'scratch_directory': self.document.get('scratch_directory', ''),
            'programs': self.document.get('modules', [])
        }
        return [cluster_item]

    def determine_dependencies(self, candidates):
        self._dependencies = []

    @property
    def uri(self):
        ssh = self.document['spec']['ssh']
        return f'{ssh["username"]}@{ssh["hostname"]}:{ssh["port"]}'

    def __repr__(self):
        return f'<{self.__class__.__name__}(filename={self.filename}, uri={self.uri})>'
