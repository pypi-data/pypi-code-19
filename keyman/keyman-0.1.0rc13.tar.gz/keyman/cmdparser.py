import argparse

from keyman.commands import commands_order
from keyman import __version__


def add_argstruct(parser, argstruct):
    parser.add_argument(
        *argstruct.names,
        **(argstruct.get_kwargs())
    )


def generate_parser():
    parser = argparse.ArgumentParser(
        description="keyman {0}".format(__version__),
        # argument_default=argparse.SUPPRESS
    )

    parser.add_argument('-v', '--version', action='version',
                        version=__version__)

    subparsers = parser.add_subparsers(
        title="available sub-commands",
        # description="description",
        # help="help info",
        # prog="subprog",
        dest="subparser",
    )

    for cmd in commands_order:
        sp = subparsers.add_parser(
            cmd.name,
            argument_default=cmd.argument_default,
            **cmd.parser_kw)
        for arg in cmd.arguments:
            # print(arg.names, arg.get_kwargs())
            add_argstruct(sp, arg)

    return parser


if __name__ == "__main__":
    print(generate_parser().parse_args(["--help"]))
    # print(generate_parser().parse_args("--test 1 insert".split()))
    # print(generate_parser().parse_args("remove --help".split()))
    # print(generate_parser().parse_args("remove --id 1 3 --nontrash".split()))
