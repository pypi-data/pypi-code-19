import logging
import umodules.helper as helper

from umodules.command import ICommand


class Status(ICommand):

    def run(self, project):
        plugin = helper.get_plugin(project, project.main)
        print('Status of Main Module [{0}] {1}'.format(project.main.name, plugin.status(project, project.main).message))
        for module in project.modules:
            if module.active:
                plugin = helper.get_plugin(project, module)
                print('Status of Module [{0}] {1}'
                      .format(module.name, plugin.status(project, module).message))

    def build(self, subparser):
        super().build(subparser)
        cmd = subparser.add_parser("status", help="...")
        cmd.set_defaults(func=self.run)
        cmd.add_argument("modules", action="store", nargs="*")
        logging.debug("- command [status] has been added to argparse")

    def activate(self):
        super().activate()

