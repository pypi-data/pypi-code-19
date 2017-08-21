"""
Generate a LocalStack composition.

Because LocalStack holds much of its state in memory, it usually makes sense to run LocalStack
in its own composition with a separate lifecycle from application services, e.g. allowing
initialization of application resources (think SNS topics and SQS queues) before starting
application services.

"""
from enum import Enum

from docker_etude.models import Network, Service, Volume
from docker_etude.sources.base import Source


class LocalStackAPI(Enum):
    SNS = 4575
    SQS = 4576

    @property
    def service_name(self):
        return self.name.lower()

    @property
    def port_mapping(self):
        return "{port}:{port}".format(
            port=self.value,
        )


class LocalStackSource(Source):

    def __init__(self,
                 region="us-east-1",
                 apis=(LocalStackAPI.SNS, LocalStackAPI.SQS,)):
        self.region = region
        self.apis = apis

    def iter_services(self, *args, **kwargs):
        yield Service(
            name="localstack",
            container_name="localstack",
            image="localstack/localstack",
            # Only include selected services (fewer resources)
            ports=[
                api.port_mapping
                for api in self.apis
            ],
            environment={
                # NB: data dir is not used for all services; state may be lost on restart
                "DATA_DIR": "/tmp/localstack/data",
                "DEFAULT_REGION": self.region,
                "HOSTNAME": "localstack",
                "SERVICES": ",".join(
                    sorted(
                        api.service_name
                        for api in self.apis
                    ),
                )
            },
            networks={
                "localstack": None,
            },
            volumes=[
                "localstack-data:/tmp/localstack/data",
            ],
        )

    def iter_networks(self, *args, **kwargs):
        """
        Generate a custom network so that other composition can connect to "localstack:port"

        """
        yield Network(
            driver="bridge",
            name="localstack"
        )

    def iter_volumes(self, *args, **kwargs):
        """
        Generate a data volume for persistent data.

        """
        yield Volume(
            name="localstack-data",
        )
