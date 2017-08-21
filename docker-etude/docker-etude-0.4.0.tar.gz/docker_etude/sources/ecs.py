"""
Generate a composition from ECS.

"""
from re import fullmatch

from boto3 import Session

from docker_etude.models import Service
from docker_etude.sources.base import Source


def paginate(func, **kwargs):
    next_token = None
    while True:
        func_kwargs = kwargs.copy()
        if next_token:
            func_kwargs.update(nextToken=next_token)
        response = func(**func_kwargs)
        yield response
        next_token = response.get("nextToken")
        if not next_token:
            break


def filter_pattern(values, pattern):
    for value in values:
        if not pattern or fullmatch(pattern, value):
            yield value


class ECSSource(Source):

    def __init__(self,
                 cluster_pattern=None,
                 profile=None,
                 region="us-east-1",
                 service_pattern=None,
                 task_pattern=None):
        self.cluster_pattern = cluster_pattern
        self.region = region
        self.profile = profile
        self.service_pattern = service_pattern
        self.task_pattern = task_pattern

    @property
    def session(self):
        return Session(
            profile_name=self.profile,
            region_name=self.region,
        )

    def iter_services(self, *args, **kwargs):
        ecs = self.session.client("ecs")
        for cluster in self.iter_ecs_cluster_arns(ecs):
            for service in self.iter_ecs_service_arns(ecs, cluster):
                for task in self.iter_ecs_task_definitions(ecs, cluster, service):
                    for container in self.iter_ecs_container_definitions(ecs, cluster, service, task):
                        yield self.make_service(container)

    def iter_ecs_cluster_arns(self, ecs):
        """
        Iterate through available clusters.

        Filter against `cluster_pattern`
BB0B
        """
        for response in paginate(ecs.list_clusters):
            clusters = response["clusterArns"]
            yield from filter_pattern(clusters, self.cluster_pattern)

    def iter_ecs_service_arns(self, ecs, cluster):
        """
        Iterate through available services

        Filter against `service_pattern`

        """
        for response in paginate(ecs.list_services, cluster=cluster):
            services = response["serviceArns"]
            yield from filter_pattern(services, self.service_pattern)

    def iter_ecs_task_definitions(self, ecs, cluster, service):
        """
        Iterate through available task definitions.

        """
        # XXX we can batch service lookups for faster speed
        services = ecs.describe_services(
            cluster=cluster,
            services=[
                service,
            ],
        )["services"]
        yield from [service["taskDefinition"] for service in services]

    def iter_ecs_container_definitions(self, ecs, cluster, service, task):
        """
        Iterate through available container definitions.

        """
        task_definition = ecs.describe_task_definition(
            taskDefinition=task,
        )
        yield from task_definition["taskDefinition"]["containerDefinitions"]

    def make_service(self, container_definition):
        return Service(
            name=container_definition["name"],
            command=container_definition.get("command"),
            container_name=container_definition["name"],
            environment={
                entry["name"]: entry["value"]
                for entry in container_definition.get("environment")
            },
            image=container_definition["image"],
        )
