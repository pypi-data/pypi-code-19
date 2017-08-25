from zope import interface

class ISparcYamlConfigContainers(interface.Interface):
    def containers(yaml_config):
        """Generator of sparc.config.IConfigContainer providers
        
        Args:
            yaml_config: Unicode valid file path to a Yaml configuration or a 
                         valid Yaml content string.
        """
    def first(yaml_config):
        """first sparc.config.IConfigContainer provider in yaml_config
        
        Args:
            yaml_config: [same as documents()]
        """