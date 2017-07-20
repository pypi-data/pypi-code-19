import logging
import pprint

import arrow

from .base import Port
from .image import Image
from .volume import Mount

LOGGER = logging.getLogger(__name__)

class Endpoint():
    "The endpoint for a service"
    def __init__(self, ports, mode='vip'):
        self.mode  = mode
        self.ports = ports

    def __eq__(self, other):
        return self.mode == other.mode and self.ports == other.ports

    @staticmethod
    def parse(payload):
        return Endpoint(
            ports = [Port.parse(p) for p in payload.get('Ports', [])],
        )

    def to_service_payload(self):
        return {
            'Mode'  : self.mode,
            'Ports' : [Port.to_service_payload(p) for p in self.ports],
        }

class Service():
    "A service in a docker swarm"
    def __init__(self, name, image, endpoint, id_=None, previous=None, version=None, mounts=None):
        self.endpoint   = Endpoint.parse(endpoint) if isinstance(endpoint, str) else endpoint
        self.id         = id_
        self.image      = Image.parse(image) if isinstance(image, str) else image
        self.mounts     = mounts or []
        self.name       = name
        self.previous   = None
        self.version    = version

    def __eq__(self, other):
        if other is None:
            return False
        return all([getattr(self, prop) == getattr(other, prop) for prop in (
            'endpoint', 'image', 'mounts')])

    def __str__(self):
        return "Service {} {}".format(self.name, self.image)

    def __repr__(self):
        return str(self)

    async def create(self, client):
        payload = self.to_payload()
        return await client.service_create(payload)

    async def update(self, client):
        await client.service_update(
            self.old.id,
            self.old.version,
            payload,
        )

    def to_payload(self):
        return {
            'EndpointSpec'      : self.endpoint.to_service_payload(),
            'Name'              : self.name,
            'TaskTemplate'      : {
                'ContainerSpec' : {
                    'Image'     : self.image.to_payload(),
                    'Mounts'    : [m.to_service_payload() for m in self.mounts],
                },
            },
        }

    @staticmethod
    def parse(payload):
        previous = payload.pop('PreviousSpec', None)
        LOGGER.debug("Parsing %s", pprint.pformat(payload))
        return Service(
            endpoint = Endpoint.parse(payload['Endpoint']),
            name     = payload['Spec']['Name'],
            id_      = payload['ID'],
            image    = payload['Spec']['TaskTemplate']['ContainerSpec']['Image'],
            mounts   = [Mount.parse(p) for p in payload['Spec']['TaskTemplate']['ContainerSpec'].get('Mounts', [])],
            previous = previous,
            version  = payload['Version']['Index'],
        )

