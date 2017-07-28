#   Copyright 2016, SpockerDotNet LLC

import argparse


def cmd_install():
    print("Hello World")


def create_options(parser):

    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help="force a command to execute with warnings",
        default=False)

    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        help="use a different configuration file",
        default="project.yml")

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        help="show more information on console when running [0-2]",
        default=0)

    parser.add_argument(
        "--version",
        action="version",
        version="",
        help="show version"
    )
    parser.add_argument(
        "--ignore-project",
        default=False,
        help=argparse.SUPPRESS
    )


def create_commands(subparser, commands):

    for command in commands:
        command.plugin_object.build(subparser)


def create_parser(commands):

    parser = argparse.ArgumentParser(prog='uModules', description="Organize your Unity Projects with uModules")
    subparser = parser.add_subparsers(dest="command")
    subparser.required = True

    create_options(parser)
    create_commands(subparser, commands)

    return parser
