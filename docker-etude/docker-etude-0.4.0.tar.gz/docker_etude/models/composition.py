"""
A docker composition.

"""
from collections import OrderedDict
from yaml import dump, load
from yaml.representer import SafeRepresenter
try:
    from yaml import CSafeDumper as SafeDumper, CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeDumper, SafeLoader
finally:
    # Register OrderedDict to dump like a regular dict
    SafeRepresenter.add_representer(OrderedDict, SafeRepresenter.represent_dict)

from docker_etude.models.base import Model
from docker_etude.models.network import Network
from docker_etude.models.service import Service
from docker_etude.models.volume import Volume


class Composition(Model):
    """
    The top-level model for a docker composition.

    Maps to/from a docker-compose.yml file.

    """
    def __init__(self,
                 networks=None,
                 services=None,
                 version="3",
                 volumes=None):
        super().__init__()
        self.version = version
        self.networks = networks or OrderedDict()
        self.services = services or OrderedDict()
        self.volumes = volumes or OrderedDict()

    def add_network(self, network):
        self.networks[network.name] = network

    def add_service(self, service):
        self.services[service.name] = service

    def add_volume(self, volume):
        self.volumes[volume.name] = volume

    def to_dict(self):
        return OrderedDict(
            version=self.version,
            networks=self.dump_model_dict(self.networks),
            services=self.dump_model_dict(self.services),
            volumes=self.dump_model_dict(self.volumes),
        )

    def dump_model_dict(self, dct):
        if not dct:
            return None

        return {
            name: model.to_safe_dict() if model else None
            for name, model in dct.items()
        }

    @classmethod
    def from_dict(cls, dct):
        return cls(
            version=dct["version"],
            networks=cls.load_model_dict(dct.get("networks"), Network),
            services=cls.load_model_dict(dct.get("services"), Service),
            volumes=cls.load_model_dict(dct.get("volumes"), Volume),
        )

    @classmethod
    def load_model_dict(cls, dct, model_cls):
        if not dct:
            return None

        return {
            name: model_cls.from_dict(dict(
                name=name,
                **model_dct
            )) if model_dct else None
            for name, model_dct in dct.items()
        }

    def to_yaml(self):
        """
        Pretty print dump as YAML.

        """
        return dump(
            self.to_safe_dict(),
            # show every document in its own block
            default_flow_style=False,
            # start a new document (via "---") before every resource
            explicit_start=True,
            # follow (modern) PEP8 max line length and indent
            width=99,
            indent=4,
            Dumper=SafeDumper,
        )

    @classmethod
    def from_yaml(cls, data):
        return cls.from_dict(
            load(data, Loader=SafeLoader),
        )
