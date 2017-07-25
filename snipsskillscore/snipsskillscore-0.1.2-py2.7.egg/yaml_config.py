# -*-: coding utf-8 -*-
""" Utilities for parsing YAML configuration files. """

import yaml


class YamlConfig:
    """ Utilities for parsing YAML configuration files. """

    def __init__(self, config='default', filename="config.yaml", default_config='default'):
        """ Initialisation.

        :param config: the key for the main configuration to look for.
        :param filename: the YAML configuration file.
        :param default_config: the default configuration, as a fallback.
        """
        self.config_tree = []
        with open(filename, 'r') as ymlfile:
            yml = yaml.load(ymlfile)
            key = config
            while key and key != default_config:
                node = yml[key]
                self.config_tree.append(node)
                try:
                    key = node["parent"]
                except (KeyError, TypeError):
                    key = default_config
            self.config_tree.append(yml[default_config])

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
        try:
            node = config[farg]
            for arg in args:
                node = node[arg]
            return node
        except (KeyError, TypeError):
            return None
