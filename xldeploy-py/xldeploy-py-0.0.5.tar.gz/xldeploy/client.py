import xldeploy.http.http_client as http
from xldeploy.service.repository import RepositoryService
from xldeploy.service.deployment import DeploymentService
from xldeploy.service.metadata import MetadataService
from xldeploy.service.tasks import TaskService
from xldeploy.service.dsl import DslService


class Client(object):
    def __init__(self, config):
        self.http_client = http.HttpClient(config)

    @property
    def repository(self):
        return RepositoryService(self.http_client)

    @property
    def deployment(self):
        return DeploymentService(self.http_client)

    @property
    def metadata(self):
        return MetadataService(self.http_client)

    @property
    def tasks(self):
        return TaskService(self.http_client)

    @property
    def dsl(self):
        return DslService(self.http_client)
