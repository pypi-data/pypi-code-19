import os
import inspect
import importlib


__author__ = 'Junya Kaneko <jyuneko@hotmail.com>'



class PluginDoesNotExist(ValueError):
    pass


def plugin(cls):    
    class PlaggubleClass:
        _PLUGGABLE_PLUGIN = True
        _PLUGGABLE_CLS_NAME = cls.__name__

        def __init__(self, *args, **kwargs):
            self._cls = cls(*args, **kwargs)

        def __getattr__(self, name):
            return getattr(self._cls, name)
        
    return PlaggubleClass


class Loader:
    def __init__(self, plugin_dirs):
        self.plugin_dirs = plugin_dirs
    
    def _list_modules(self):
        modules = []
        for plugin_dir in self.plugin_dirs:
            for file_name in os.listdir(plugin_dir):
                if file_name.endswith('.py') and file_name != '__init__.py':
                    modules.append(
                        importlib.machinery.SourceFileLoader(
                            'pluggable.%s'
                            % (file_name[:-3]), os.path.join(plugin_dir, file_name)).load_module())
        return modules

    def _list_plugins(self):
        plugins = []
        for module in self._list_modules():
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if getattr(cls, '_PLUGGABLE_PLUGIN', False):
                    plugins.append(cls)
        return plugins
                
    def load(self, name, original=True, *args, **kwargs):
        for plugin in self._list_plugins():
            if plugin._PLUGGABLE_CLS_NAME  == name:
                if original:
                    return plugin(*args, **kwargs)._cls
                else:
                    return plugin(*args, **kwargs)
        raise PluginDoesNotExist

