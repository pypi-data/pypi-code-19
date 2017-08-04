# coding: utf-8
"""
Contains the class Factory.
"""

from .singleton import Singleton
from .dependency import Dependency


class Factory(object):
    """
    This class handles the build of the different objects from the application.
    """
    def __init__(self, config):
        self._config = config
        self._singletons = {}

    def build(self, *args, **kwargs):
        """
        Build a class regarding the arguments given in parameters.
        The script look for a class_path parameter first, then add parameters from
        the configuration, and finally the optional parameters given.
        Args:
            args (list): Arguments as a list.
            kwargs (dict): Positionnal arguments as a dict.
        Return:
            (object): The instancied class.
        """

        kwargs = kwargs or {}

        class_path = kwargs.get(u"class_path", None) or args[0]
        if len(args) > 0 and args[0] == class_path:
            args = args[1:]
        if u"class_path" in kwargs:
            del kwargs[u"class_path"]

        try:
            class_def, params = self.find(self._config, class_path)
        except KeyError:
            raise ValueError(u"Can't find path in factory for {}.".format(class_path))
        params, is_singleton = self.interpret_params(params)
        kwargs.update(params)

        if is_singleton:
            if class_path not in self._singletons:
                self._singletons[class_path] = class_def(*args, **kwargs)
            return self._singletons.get(class_path)
        else:
            return class_def(*args, **kwargs)

    def interpret_params(self, params):
        """
        Short cut to parse parameters from the config.
        Args:
            params (dict): The list of parameters.
        Return:
            (dict, bool): The parameters, and a flag if it is a singleton or not.
        """
        is_singleton = False
        if isinstance(params, Singleton):
            is_singleton = True
            params = params.params

        for key, dependency in params.items():
            if isinstance(dependency, Dependency):
                params[key] = dependency.inject(factory=self)

        return params, is_singleton

    def find(self, obj, path):
        """
        Tries to find an object in the factory regarding the given path.
        Args:
            obj (object): Corresponding to the dict usued as a configuration for the factory.
            path (unicode): The path to the object in the configuration.
        Return:
            (type): The class def.
        """
        tab = path.split(u".")
        current_key, other = tab[0], tab[1:]

        if isinstance(current_key, unicode):
            for key in obj:
                if not isinstance(key, unicode) and key.__name__ == current_key:
                    current_key = key
                    break

        if not other and current_key:
            return current_key, obj[current_key]
        elif other:
            return self.find(obj[current_key], u".".join(other))
