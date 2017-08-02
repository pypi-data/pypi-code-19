# -*-: coding utf-8 -*-
""" Utilities for parsing YAML configuration files. """

import yaml


class YamlConfig:
    """ Utilities for parsing YAML configuration files. """

    def __init__(self,
                 filename="config.yaml",
                 yaml_config=None,
                 config_key='default'):
        """ Initialisation.

        :param filename: the YAML configuration file.
        :param yaml_config: a loaded YAML configuration (instead of a file).
        :param config_key: the key for the main configuration to look for.
        """
        if filename is not None:
            with open(filename, 'r') as ymlfile:
                yaml_config = yaml.load(ymlfile)
        self.load(yaml_config, config_key)

    def load(self, yaml_config, config_key):
        """ Load a YAML configuration tree.

        :param yaml_config: a loaded YAML configuration.
        :param config_key: the key for the main configuration to look for.
        """
        default_config = 'default'
        self.config_tree = []
        key = config_key
        while key and key != default_config:
            node = yaml_config[key]
            self.config_tree.append(node)
            try:
                key = node["parent"]
            except (KeyError, TypeError):
                break
        try:
            self.config_tree.append(yaml_config[default_config])
        except (KeyError, TypeError):
            pass

    def get_item(self, farg, *args):
        """ Get the value of an item for a given search path, looking for parent
            values if not found in the item itself.

            Example: given a config

            ```
            default:
                locale: fr_FR
            my_setup:
                mqtt_broker:
                    hostname: localhost
            ```

            we look for the `my_setup` config:

            >>> yaml = YamlConfig('my_setup')

            # The following will return "localhost":
            >>> yaml.get_item('mqtt_broker', 'hostname')

            # The following will look at the default configuration
            # and return "fr_FR":
            >>> yaml.get_item('locale')
        """
        if not self.config_tree or len(self.config_tree) == 0:
            return None
        for config in self.config_tree:
            item = YamlConfig.get_config_item(config, farg, args)
            if item is not None:
                return item
        return None

    @staticmethod
    def get_config_item(config, farg, args):
        """ Given a search path, return the value at the end node, or None.

        :param config: the config to look at.
        :param farg, args: the search path, i.e. a list of keys k1,...,kn.
        :return: the value `yaml[k1][k2]...[kn]` if it exists, or None.
        """
        if config is None:
            return None
        try:
            node = config[farg]
            for arg in args:
                node = node[arg]
            return node
        except (KeyError, TypeError):
            return None
