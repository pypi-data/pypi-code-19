"""Tool that invokes the given command.

If the given command is given with a relative path, then this is
interpreted as a project local, and the failure is determined by the
``--if-no-op`` flag.

"""
import argparse
import logging

from menhir.tool import Tool
from menhir.tool_utils import OK, FAIL, NOTHING_TO_DO, tool_env, working_dir

log = logging.getLogger(__name__)


def tool():
    return Exec()


class Exec(Tool):

    def dir_info(tool, path, info):
        return {
            'project_recognised': False,
            'can_run': True,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        """Arg parser for the tool options and arguments."""
        return parser(**kwargs)

    def execute_tool(tool, path, info, args):
        """Execute the script tool."""
        import os
        from os.path import basename, isabs
        import subprocess

        with working_dir(path):
            command = args.command_name
            if basename(command) != command and not isabs(command):
                if (
                        not os.access(command, os.X_OK)
                ):
                    return NOTHING_TO_DO

            cmd = [command] + args.command_args
            log.info('Running "%s" in %s', " ".join(cmd), path)
            if 'changed' in info and not (
                    info['changed'].get('self') or
                    info['changed'].get('dependents')
            ):
                return OK

            env = tool_env()
            changed = info.get('changed')
            if changed is None:
                env['MENHIR_ALL'] = "1"
            else:
                if changed.get('self'):
                    env['MENHIR_CHANGED_SELF'] = "1"
                if changed.get('dependents'):
                    env['MENHIR_CHANGED_DEPENDENTS'] = "1"
                if changed.get('dependees'):
                    env['MENHIR_CHANGED_DEPENDEES'] = "1"

            result = subprocess.call(cmd, env=env)
            log.debug('Exec %s result: %s', args.command_name, result)
            if result:
                return FAIL
            return OK


def parser(**kwargs):
    """Arg parser for the tool options and arguments."""
    parser = argparse.ArgumentParser(
        description="Execute command.",
        **kwargs
    )
    parser.add_argument(
        'command_name',
        metavar='command-name',
        help="""Command to invoke from bin directory.

If this includes a relative path it is interpreted as being project
local, and if it doesn't exist, then failure failure is determined by
the ``--if-no-op`` flag """
    )
    parser.add_argument(
        'command_args',
        nargs=argparse.REMAINDER,
        help='command arguments'
    )
    return parser
