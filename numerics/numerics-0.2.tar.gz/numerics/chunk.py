#!/usr/bin/env python

# imports
import argparse
import sys

def chunk(n, *args):
    """
    split `args` into `n` parts
    """

    args =list(args)
    step = len(args)/int(n)
    retval = []
    for i in range(n-1):
        retval.append(args[i*step:(i+1)*step])
    retval.append(args[(n-1)*step:])
    return retval


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = argparse.ArgumentParser(description=chunk.__doc__)
    parser.add_argument('args', nargs='*')
    parser.add_argument('-n', dest='n',
                        type=int, default=1,
                        help="number of parts to split into [DEFAULT: %(default)s]")
    options = parser.parse_args(args)

    # split
    chunks = chunk(options.n, *options.args)

    # output
    for _chunk in chunks:
         print _chunk

if __name__ == '__main__':
    main()
