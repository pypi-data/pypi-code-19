#!/usr/bin/env python

"""
create index.ini file from directory listings
"""

#ls -1 | while read line; do echo "${line} = ${line}"; done > index.ini

# imports
import argparse
import os
import sys


class CreateIndex(object):
    """
    decoupage directory index .ini creation
    """
    # TODO: maybe this should inherit or otherwise extend
    # some more abstract Index class

    def __init__(self, directory):
        assert os.path.isdir(directory)
        self.directory = directory

    def __str__(self):
        lines = ['{item}={item}'.format(item=item)
                 for item in sorted(os.listdir(self.directory))]
        return '\n'.join(lines) + '\n'


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--directory',
                        default=os.getcwd(),
                        help="directory to create index for (current working directory by default)")
    options = parser.parse_args(args)

    print(CreateIndex(options.directory))


if __name__ == '__main__':
    main()
