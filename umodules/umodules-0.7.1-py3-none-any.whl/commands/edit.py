
import logging
import os
import umodules.helper as helper

from umodules.command import ICommand


def _edit(project):
    try:
        project_path = '{0}'.format(project.project_path)
        project_path = os.path.abspath(project_path)
        cmd = helper.build_unity_command(project.unity_path)
        cmd = '{0} -projectPath "{1}"'.format(cmd, project_path)
        print('Opening Project [{0}]'.format(project.name))
        helper.run_background_command(cmd)
    except Exception as e:
        raise Exception(e)


class Install(ICommand):

    def run(self, project):
        _edit(project)

    def build(self, subparser):
        super().build(subparser)
        cmd = subparser.add_parser("edit", help="...")
        cmd.set_defaults(func=self.run)
        logging.debug("- command [edit] has been added to argparse")

    def activate(self):
        super().activate()

