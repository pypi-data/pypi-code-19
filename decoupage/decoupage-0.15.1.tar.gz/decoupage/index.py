#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
index.ini
"""

import argparse
import os
import sys

here = os.path.dirname(os.path.realpath(__file__))

def index(directory):
    """
    returns string representation of directory
    """

    return '\n'.join(['{name} = {name}'.format(name=name)
                      for name in sorted(os.listdir(directory),
                                         key=lambda name: name.lower())
                      if not name.startswith('.')])


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', help='directory')
    parser.add_argument('-o', '--output', dest='output',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help='output')
    options = parser.parse_args(args)

    # sanity
    if not os.path.isdir(options.directory):
        parser.error("Not a directory: '{}'".format(options.directory))

    # output
    options.output.write(index(options.directory))


if __name__ == '__main__':
    main()
