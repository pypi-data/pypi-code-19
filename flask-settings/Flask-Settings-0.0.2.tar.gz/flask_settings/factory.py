# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import types

from flask_settings.basic import BasicConfig


class ConfigFactory(object):

    @staticmethod
    def _get_config_module(filename):
        """
        Load module by filename from settings package.
        The same trick is used by Flask for its config.
        :param filename: str
        :return: module
        """
        m = types.ModuleType(str('settings'))
        m.__file__ = filename
        try:
            with open(filename) as config_file:
                # pylint: disable=exec-used
                exec(compile(config_file.read(), filename, 'exec'), m.__dict__)
        except IOError as e:  # pragma: no cover
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise e
        return m

    @classmethod
    def _get_config_class(cls, filename):
        """
        Load the first config class from the module
        by module's file name from settings package.
        :param filename: str
        :return: class
        """
        module_ = cls._get_config_module(filename)
        for attr_name in dir(module_):
            class_ = getattr(module_, attr_name)
            if (isinstance(class_, type) and
                    issubclass(class_, BasicConfig) and
                    # pylint: disable=no-member
                    class_.__module__ == module_.__name__):
                return class_

    def __call__(self, app=None, name=None):
        """
        Factory method that returns instance of the config class.
        When Flask application instance is set, it will be configured
        with loaded config object.
        :param app: Flask application instance
        :param name: str, config name
        :return: instance of config class
        """
        config_name = name or os.getenv('FLASK_SETTINGS', 'default')
        filename = os.path.join(app.root_path, 'settings', config_name + '.py')
        config_class = self._get_config_class(filename)
        return config_class(app)


Settings = ConfigFactory()
