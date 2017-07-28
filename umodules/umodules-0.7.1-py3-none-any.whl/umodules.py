#   Copyright 2016, SpockerDotNet LLC

import logging
import sys
import os

import umodules
import umodules.parser as parser
import umodules.project as project

from umodules.config import Config


def _get_logging_level():
    #   default logging level
    level = logging.ERROR

    #   check args for -v or --verbose
    i = 0
    for arg in sys.argv:
        i += 1
        if arg == '-v' or arg == '--verbose':
            if sys.argv[i].isnumeric():
                l = int(sys.argv[i])
                if l == 0:
                    level = logging.WARNING
                if l == 1:
                    level = logging.INFO
                if l == 2:
                    level = logging.DEBUG

    return level


def init():

    #   setup logging
    logging.basicConfig(
        filename="./umodules.log",
        level=_get_logging_level(),
        format='[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)',
        datefmt='%m/%d/%Y %I:%M:%S %p')

    #   add console logging
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    #   reduce Yapsy logging
    logging.getLogger("yapsy").setLevel(logging.ERROR)

    #   some diagnostic info
    logging.debug(sys.path)

    #   a little welcome message
    logging.log(99, umodules.__logo__)
    logging.log(99, 'Version ' + umodules.__version__ + ', ' + umodules.__copyright__)
    print()


def create_paths(proj):
    #   define repository path
    proj.repository_path = os.path.abspath('.repo/{0}'.format(proj.name))

    #   define project path
    proj.project_path = os.path.abspath('{0}/{1}'.format(proj.project_path, proj.name))

def create_home_path(proj):
    #   define the home path aka where am i running from?
    proj.home_path = os.path.abspath(os.path.dirname(__file__))


def main():
    try:
        #   initialize the command
        init()

        #   create config object
        config = Config()

        #   find all plugins
        config.load_plugins()

        #   get all module types plugins
        module_types = config.get_modules()

        #   get all command plugins
        commands = config.get_commands()

        #   get tokens
        tokens = config.load_tokens()

        #   get options
        options = config.load_options()

        #   add commands to the parser
        args = parser.create_parser(commands).parse_args()

        #   create the project from the project file
        proj = project
        # proj = project.load(args.config, tokens)
        if not (args.ignore_project):
            #   load project config
            proj = project.load(args.config, tokens)
            #   set the available project module types
            proj.module_types = module_types
            # set the project paths
            create_paths(proj)

        create_home_path(proj)

        #   add list of module parameters
        modules = None
        opts = vars(args)
        if 'modules' in opts:
            modules = opts['modules']
        proj.module_names = modules

        #   execute command with project object
        proj.args = args
        proj.options = options
        args.func(proj)

        exit(0)

    except Exception as e:
        logging.error(e)
        logging.error('Operation Cancelled')
        exit(1)
