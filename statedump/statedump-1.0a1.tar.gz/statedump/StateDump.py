"""

"""

import os
import sys
import random
import argparse
import pathspec


class State:
    """This class does nothing!"""
    def __init__(self, *args, **kwargs):
        pass


def main():
    parser = argparse.ArgumentParser(description = "StateDump")
    parser.add_argument(dest = 1,
                        nargs = 1,
                        metavar = "<directory>",
                        help = "specify the target directory")
    parser.add_argument("-I", "--ignore-file",
                        nargs = 1,
                        metavar = "<ignore_file>",
                        help = "specify name of .xxignore file. "
                               "By default, `.sdignore` and `.gitignore` will be recognized")
    parser.add_argument("--stdout",
                        action = "store_true",
                        help = "also write the generated script to stdout")
    parser.add_argument("--stderr",
                        action = "store_true",
                        help = "also write the generated script to stderr")
    parser.add_argument("-n", "--no-file",
                        action = "store_true",
                        help = "do not write the generated script to file")
    parser.print_help()


"""
if os.name != "posix":
    raise Exception("`StateDump` only supports 'posix' systems, but current is '%s'." % os.name)
"""

if __name__ == "__main__":
    main()
