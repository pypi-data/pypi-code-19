import argparse


class Command:
    # Class variables:
    # name of the sub-command, useful when add_parser() is called for the
    # subparsers created by argparse.ArgumentParser.add_subparsers().
    name = ""

    # Some keyword arguments for add_parser() which is called for the
    # subparsers created by argparse.ArgumentParser.add_subparsers().
    parser_kw = {
        'usage': "",
        'description': "",
        'help': "",
    }

    argument_default = argparse.SUPPRESS

    # list of arguments (represented by keyman.cmdparser.ArgStruct)
    arguments = []

    # tell the cmd parser whether a help message of this command will be printed
    # when the command accepts no arguments, i.e. "$ keyman command_name"
    noargs_for_help = True

    def __init__(self):
        pass

    def run(self, dbhandler):
        # Must be implemented.
        raise NotImplemented
