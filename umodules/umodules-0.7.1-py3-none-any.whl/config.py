#   Copyright 2016, SpockerDotNet LLC

import logging
import os
import yaml
import io

from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManager

# from .commands.command import ICommand
# from .module_types.module import IModuleType

from umodules.command import ICommand
from umodules.module_type import IModuleType


class Config(object):

    def __init__(self):
        self.manager = PluginManager()

    def load_plugins(self):
        """
        Returns a Dictionary of Module Plugins

        :return: A Dictionary of Modules
        """

        #   create plugin manager and set categories
        self.manager.setCategoriesFilter({
            "Default": IPlugin,
            "Modules": IModuleType,
            "Commands": ICommand,
        })

        #   build path to module_types
        this_dir = os.path.abspath(os.path.dirname(__file__))
        module_plugin_dir = os.path.join(this_dir, 'module_types')
        command_plugin_dir = os.path.join(this_dir, 'commands')
        places = [module_plugin_dir, command_plugin_dir]
        self.manager.setPluginPlaces(places)

        logging.debug("- searching for plugins at {0}".format(places))

        #   our default extension is '.plugin'
        self.manager.setPluginInfoExtension("plugin")

        #   collect all plugins
        self.manager.collectPlugins()

        #   activate and initialize all module plugins
        for pluginInfo in self.manager.getAllPlugins():
            self.manager.activatePluginByName(pluginInfo.name)
            logging.debug("- plugin [{0}] has been activate".format(pluginInfo.name))
            module = pluginInfo.plugin_object
            module.plugin_name = pluginInfo.name

    def get_modules(self):
        return self.manager.getPluginsOfCategory("Modules")

    def get_commands(self):
        return self.manager.getPluginsOfCategory("Commands")

    def load_tokens(self):

        hf = os.path.abspath(os.path.expanduser("~") + "/.umodules")
        pf = os.path.abspath('.umodules')

        logging.debug('- looking for [.umodules] file in Project folder [{0}]'.format(pf))

        if os.path.exists(pf):
            logging.debug('- found it')
            file = io.open(pf)
            text = file.read()
            data = yaml.load(text)
            return(data['umodules'])

        logging.debug('- looking for [.umodules] file in Home folder [{0}]'.format(hf))

        if os.path.exists(hf):
            logging.debug('- found it')
            file = io.open(hf)
            text = file.read()
            data = yaml.load(text)
            return(data['umodules'])


    def load_options(self):
        hf = os.path.abspath(os.path.expanduser("~") + "/.umodules")
        pf = os.path.abspath('.umodules')

        logging.debug('- looking for [.umodules] file in Project folder [{0}]'.format(pf))

        if os.path.exists(pf):
            logging.debug('- found it')
            file = io.open(pf)
            text = file.read()
            data = yaml.load(text)
            return(data['options'])

        logging.debug('- looking for [.umodules] file in Home folder [{0}]'.format(hf))

        if os.path.exists(hf):
            logging.debug('- found it')
            file = io.open(hf)
            text = file.read()
            data = yaml.load(text)
            return(data['options'])

