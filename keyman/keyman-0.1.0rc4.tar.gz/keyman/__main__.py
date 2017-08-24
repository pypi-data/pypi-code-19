import sys

from keyman.cmdparser import generate_parser
from keyman.handler.confighandler import init_local_dir
from keyman.commands import commands_dict
from keyman.handler.dbhandler import DBHandler


def main(args=None):
    # main(), e.g. command line used
    if args is None:
        args = sys.argv[1:]

    # print(args)

    # Include the case: if command line is used, but sys.argv[1:] = []
    # i.e. "$ keyman.py"
    # and cases where main([]) is called in some scripts.
    # Note that argparse will take no actions when there is no arguments given
    # if we don't manually deal with this case.
    if not args:
        args = ["--help"]

    parser = generate_parser()
    result = parser.parse_args(args)

    if not result.subparser:  # no sub-commands
        parser.parse_args(args)
        # If there are some arguments for the main command (keyman) other than
        # "--help" and "--version", we need to process them here.
        # Note that a "help" or "version" option will cause an system exit after
        # the help / version messages are printed out.
        return
    else:
        command_name = result.subparser
        command = commands_dict[command_name]
        result = vars(result)
        result.pop("subparser")
        # print(result)

        if result == {} and command.noargs_for_help:
            parser.parse_args([command_name, "--help"])
            return

        c = command(**result)

        conn = init_local_dir()
        dbhandler = DBHandler(conn)

        c.run(dbhandler)

        conn.close()
        return
