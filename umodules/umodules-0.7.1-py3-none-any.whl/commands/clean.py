#   Copyright 2016, SpockerDotNet LLC

import logging
import umodules.helper as helper

from umodules.command import ICommand


def __get_module(project, name):
    for module in project.modules:
        if name.lower() == module.name.lower():
            return module
    raise Exception('Module {0} Not Found'.format(module.name))


def _clean_modules(project):
    logging.debug('- cleaning modules')
    for name in project.module_names:
        module = __get_module(project, name)
        helper.clean_module(project, module)


def _clean_all_modules(project):
    logging.debug('- cleaning all modules')
    for module in project.modules:
        helper.clean_module(project, module)


def _run(project):

    if project.args.command == 'clean':
        #   if no module specified, remove all modules
        if len(project.module_names) > 0:
            _clean_modules(project)
        #   or, remove modules specified on the cli
        else:
            _clean_all_modules(project)

    if project.args.command == 'cleanall':
        logging.log(99, "Removing Project {0}".format(project.name))
        helper.clean_all(project)


class Clean(ICommand):

    def run(self, project):
        _run(project)

    def build(self, subparser):

        #   add clean command
        super().build(subparser)
        cmd = subparser.add_parser("clean", help="...")
        cmd.set_defaults(func=self.run)
        cmd.add_argument("modules", action="store", nargs="*")
        logging.debug("- command [clean] has been added to argparse")

        #   add clean all command
        super().build(subparser)
        cmd = subparser.add_parser("cleanall", help="Help For Cleanall")
        cmd.set_defaults(func=self.run)
        logging.debug("- command [cleanall] has been added to argparse")

    def activate(self):
        super().activate()

