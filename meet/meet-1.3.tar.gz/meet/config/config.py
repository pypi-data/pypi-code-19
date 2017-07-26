#!/bin/usr/python
# config.py

import sys
import os
import os.path

from configparser import ConfigParser

home_dir = os.path.expanduser('~')
config_dir = os.path.join(home_dir, '.config')
configfile_name = os.path.join(config_dir, 'meet_config.ini')
client_secret_file_location = os.path.join(config_dir)


class AppConf:
    '''Represents all display options and setup parameters.  Provides the
    ability for a user to create their base config file, and then always
    consume the latest configurations upon app load'''

    def __init__(self):
        # Determine what system platform is in use
        if sys.platform.startswith('linux'):
            self.basic_editor = 'vi'
        elif sys.platform == 'win32' or sys.platform == 'cygwin':
            self.basic_editor = 'edit'
        elif sys.platform == 'darwin':
            self.basic_editor = 'vi'
        else:
            self.basic_editor = 'vi'
        self.check_for_config_file()
        self.configs = self.get_configurations()

    def check_for_config_file(self):
        if not os.path.isfile(configfile_name):
            # Create the configuration file as it doesn't exist yet
            cfgfile = open(configfile_name, 'w')

            # Add content to the file
            config = ConfigParser()
            config.add_section('setup')
            config.set(
                'setup',
                'client_secret_file_name',
                'meet_client_secret.json'
            )
            config.set(
                'setup',
                'client_secret_file_location',
                client_secret_file_location
            )
            config.add_section('options')
            config.set(
                'options',
                'open_markdown_editor',
                'true'
            )
            config.set(
                'options',
                'editor_cli_command',
                self.basic_editor
            )
            config.write(cfgfile)
            cfgfile.close()
            print('\nA configuration file was created with default values\n')
            print('The file is located at: {}\n'.format(configfile_name))
            inp = input('Press <Enter> to continue.')

    def get_configurations(self):
        parser = ConfigParser()
        parser.read(configfile_name)
        confs = {}
        for section_name in parser.sections():
            for key, value in parser.items(section_name):
                confs[key] = value
        return confs
