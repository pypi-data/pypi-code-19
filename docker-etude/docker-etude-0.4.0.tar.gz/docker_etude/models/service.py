"""
A docker compose service.

"""
from collections import OrderedDict

from docker_etude.models.base import Model


class Service(Model):
    """
    A single docker compose service.

    """
    def __init__(self,
                 image,
                 command=None,
                 container_name=None,
                 depends_on=None,
                 deploy=None,
                 environment=None,
                 links=None,
                 name=None,
                 networks=None,
                 ports=None,
                 ulimits=None,
                 volumes=None):
        """
        Build a service definition.

        The service minimally needs an image name. The service should also known its name
        (from the left-hand-side of the composition's "services" mapping) because most/many
        composition transformations will need to know this name.

        :param image: the image name (required)
        :param name: the service's name in the composition definition (strongly encouraged)

        """
        super().__init__()
        self.name = name
        self.image = image
        self.command = command
        self.container_name = container_name
        self.depends_on = depends_on
        self.deploy = deploy
        self.environment = environment or {}
        self.links = links or []
        self.networks = networks or {}
        self.ports = ports or []
        self.ulimits = ulimits or {}
        self.volumes = volumes or []

    def to_dict(self):
        return OrderedDict(
            command=self.command,
            container_name=self.container_name,
            depends_on=self.depends_on,
            deploy=self.deploy,
            environment=self.environment,
            image=self.image,
            links=self.links,
            networks=self.networks if self.networks else None,
            ports=self.ports,
            ulimits=self.ulimits,
            volumes=self.volumes,
        )

    @classmethod
    def from_dict(cls, dct):
        return cls(
            command=dct.get("command"),
            container_name=dct.get("container_name"),
            depends_on=dct.get("depends_on"),
            deploy=dct.get("deploy"),
            environment=dct.get("environment"),
            image=dct["image"],
            links=dct.get("links"),
            name=dct.get("name"),
            networks=dct.get("networks"),
            ports=dct.get("ports"),
            ulimits=dct.get("ulimits"),
            volumes=dct.get("volumes"),
        )
