from os.path import isfile
import yaml
from zope import interface

from sparc.config.container import SparcConfigContainer
from .interfaces import ISparcYamlConfigContainers

@interface.implementer(ISparcYamlConfigContainers)
class SparcYamlConfigContainers(object):

    def containers(self, yaml_config):
        config = yaml_config if not isfile(yaml_config) else open(yaml_config)
        for doc in yaml.load_all(config):
            yield SparcConfigContainer(doc)

    def first(self, yaml_config):
        return next(self.containers(yaml_config))