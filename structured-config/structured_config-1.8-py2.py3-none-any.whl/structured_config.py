__author__ = "Andrew Leech"
__copyright__ = "Copyright 2017, alelec"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Andrew Leech"
__email__ = "andrew@alelec.net"

import os
import sys
import yaml
import wrapt
import inspect
import appdirs
import logging


class ConfigFile(object):
    def __init__(self, config_path, config, appname=None):
        """
        Config file container.
        :param str config_path: path to file for storage. Either absolute
                                 or relative. If relative, appname is required
                                 to determine user config folder for platform
        :param Structure config: top level config item
        :param str appname: When using relative path fon config_file, 
                             appname is required for user config dir
        """
        self.write_enabled = False
        self.config_path = config_path
        # convert passed in config to a registered instance
        self.config = self.register_structure(config)
        assert isinstance(self.config, (config, type(config)))
        log = logging.getLogger("Config")

        if not os.path.isabs(self.config_path):
            if not appname:
                raise ValueError("Must provide appname for relative config file path")
            appdir = appdirs.user_data_dir(appname=appname)
            if not os.path.exists(appdir):
                try:
                    os.makedirs(appdir)
                except:
                    pass
            self.config_path = os.path.join(appdir, self.config_path)

        ## Startup
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as configfile:
                self.config = self.register_structure(yaml.load(configfile))
                log.info("Loaded config from %s" % self.config_path)

        self.write_enabled = True

        # Ensure the config file exists for new installations.
        if not os.path.exists(self.config_path):
            self.write_yaml()
            log.info("Initialised new config file at %s" % self.config_path)

    def write_yaml(self):
        if self.write_enabled:
            try:
                os.makedirs(os.path.dirname(self.config_path))
            except OSError:
                pass
            with open(self.config_path, 'w') as configfile:
                yaml.dump(self.config, configfile, default_flow_style=False)

    def register_structure(self, structure):
        """
        This will attach this config files' writer to the structure
        :param Structure structure: key to register
        :returns: structure as passed in
        """
        def attach(_structure):
            if inspect.isclass(_structure) and issubclass(_structure, Structure):
                _structure = _structure()
            if isinstance(_structure, Structure):
                _structure.register_config_file(self)

            return _structure

        structure = attach(structure)

        for key, val in structure:
            if isinstance(val, dict):
                for k, v in val.items():
                    val[k] = attach(v)

            elif isinstance(val, (list, set, tuple)):
                val = List((attach(v) for v in val))
                val.register_config_file(self)

            else:
                val = attach(val)
            structure[key] = val

        return structure


class Structure(object):
    def __init__(self, **kwargs):
        cls = self.__class__
        # Set the yaml name of the class
        self._yaml_tag = '!' + cls.__name__
        self._config_file = None  # type: ConfigFile

        # Ensure instance has copy of attributes from class
        self.__dict__.update({k:v for k,v in cls.__dict__.items()
                              if not k.startswith('_')})

        self.__dict__.update(kwargs)

        yaml.add_constructor(self._yaml_tag, cls._from_yaml)
        yaml.add_representer(cls, self._to_yaml)


    @classmethod
    def _from_yaml(cls, loader, node):
        return loader.construct_yaml_object(node, cls)

    def _to_yaml(self, dumper, data):
        return dumper.represent_yaml_object(self._yaml_tag, data, self.__class__, flow_style=False)

    def register_config_file(self, config_file):
        self._config_file = config_file

    def __iter__(self):
        for key, val in self.__dict__.items():
            yield key, val

    def __contains__(self, item):
        return item in self.__dict__

    def __hasattr__(self, key):
        return key in self.__dict__
        
    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, val):
        return self.__setattr__(item, val)

    def __setattr__(self, key, value):
        value = value.value if isinstance(value, TypedField) else value
        if not hasattr(self, key):
            changed = True
            super().__setattr__(key, value)
        else:
            try:
                current = self.__dict__[key]
            except KeyError:
                current = self.__getattribute__(key, raw=True)

            if isinstance(current, TypedField):
                current.converter(value)  # Ensure the value is valid
                changed = value != current
                current.value = value
            else:
                changed = not hasattr(self, key) or value != current
                super().__setattr__(key, value)

        # Write out the yaml on each attribute update
        if changed and not key.startswith('_') and self._config_file:
            self._config_file.write_yaml()

    def __getattribute__(self, item, raw=False):
        current = object.__getattribute__(self, item)
        if not raw and isinstance(current, TypedField):
            return current.converter(current.value)
        return current

    def __repr__(self):
        return "%s: %s" % (self.__class__.__name__, self.__dict__)

    def __eq__(self, other):
        if isinstance(other, Structure):
            other = other.__getstate__()
        return self.__getstate__() == other

    def __getstate__(self):
        return {key: val for key, val in self.__dict__.items() if not key.startswith('_')}

    def to_dict(self):
        def _dict(val):
            if isinstance(val, Structure):
                val = val.to_dict()
            elif isinstance(val, List):
                val = [_dict(val) for val in list(val)]
            return val

        return {key: _dict(self[key]) for key, val in self if not key.startswith('_')}
    
    def update(self, data, conf=None):
        conf = self if conf is None else conf
        for key, val in data.items():
            if (not key.startswith('_') and
                        key != '$$hashKey' and
                        key in conf):
                if isinstance(val, dict):
                    self.update(val, conf[key])
                elif isinstance(val, list):
                    for idx, lval in enumerate(val):
                        self.update(lval, conf[key][idx])
                else:
                    conf[key] = val

class List(list):
    """
    Overridden list to allow us to wrap functions for automatic write.
    This is required as we can't wrap/replace the builtin list functions
    """
    yaml_tag = '!list'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config_file = None  # type: ConfigFile

    def register_config_file(self, config_file):
        self._config_file = config_file
        wrapt.wrap_function_wrapper(self, 'clear', self.write_after)
        wrapt.wrap_function_wrapper(self, 'extend', self.write_after)
        wrapt.wrap_function_wrapper(self, 'pop', self.write_after)
        wrapt.wrap_function_wrapper(self, 'remove', self.write_after)
        wrapt.wrap_function_wrapper(self, 'append', self.write_after)
        wrapt.wrap_function_wrapper(self, 'insert', self.write_after)

    def write_after(self, wrapped, instance, args, kwargs):
        ret = wrapped(*args, **kwargs)
        if self._config_file:
            self._config_file.write_yaml()
        return ret

    def __getstate__(self):
        return list(self)


def list_rep(dumper, data):
    """
    Ensure pyyaml treats our list as a regular list
    """
    return dumper.represent_list(list(data))


yaml.add_representer(List, list_rep)


class TypedField(object):
    def __init__(self, value, converter):
        self.value = value
        self.converter = converter

        cls = self.__class__
        self._yaml_tag = '!' + cls.__name__

        yaml.add_constructor(self._yaml_tag, self._from_yaml)
        yaml.add_representer(cls, self._to_yaml)

    def __getstate__(self):
        return dict(value=self.value, converter=self.converter)

    def __setstate__(self, state):
        self.__dict__.update(state)

    @classmethod
    def _from_yaml(cls, loader, node):
        return loader.construct_yaml_object(node, cls)

    def _to_yaml(self, dumper, data):
        return dumper.represent_yaml_object(self._yaml_tag, data, self.__class__, flow_style=False)



class IntField(TypedField):
    def __init__(self, value):
        super(IntField, self).__init__(value, int)
