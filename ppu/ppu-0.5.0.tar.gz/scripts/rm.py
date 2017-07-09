#! /usr/bin/env python

import argparse
import os
import shutil

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove old files')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='remove directories recursively')
    parser.add_argument('names', nargs='+',
                        help='files/directories names to remove')
    args = parser.parse_args()

    for name in args.names:
        if os.path.isdir(name):
            if args.recursive:
                shutil.rmtree(name)
            else:
                os.rmdir(name)
        else:
            os.unlink(name)
