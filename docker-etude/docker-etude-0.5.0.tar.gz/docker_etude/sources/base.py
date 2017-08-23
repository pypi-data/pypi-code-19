"""
A composition source.

"""
from docker_etude.models.composition import Composition


class Source:
    """
    A source is a generator for services, networks, and volumes.

    """
    def load(self, *args, **kwargs):
        composition = Composition()

        for network in self.iter_networks(*args, **kwargs):
            composition.networks[network.name] = network

        for service in self.iter_services(*args, **kwargs):
            composition.services[service.name] = service

        for volume in self.iter_volumes(*args, **kwargs):
            composition.volumes[volume.name] = volume

        return composition

    def iter_services(self, *args, **kwargs):
        return
        yield

    def iter_networks(self, *args, **kwargs):
        return
        yield

    def iter_volumes(self, *args, **kwargs):
        return
        yield
