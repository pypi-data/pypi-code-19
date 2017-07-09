#!/usr/bin/env python

from __future__ import print_function
import argparse
from datetime import datetime, timedelta
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove old files')
    parser.add_argument('-e', '--empty-dirs', action='store_true',
                        help='remove empty directories')
    parser.add_argument('-o', '--older', required=True, type=int,
                        help='remove files older than this (in days)')
    parser.add_argument('start_dir', help='start from this directory')
    args = parser.parse_args()

    count = errors = size = 0
    now = datetime.now()

    for dirpath, dirnames, filenames in os.walk(args.start_dir, topdown=False):
        has_newer_files = False
        for fname in filenames:
            file_path = os.path.join(dirpath, fname)
            file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_modified + timedelta(days=args.older) < now:
                count += 1
                size += os.path.getsize(file_path)
                try:
                    os.remove(file_path)
                except OSError:
                    errors += 1
            else:
                has_newer_files = True
        if args.empty_dirs and not dirnames and not has_newer_files:
            count += 1
            try:
                os.rmdir(dirpath)
            except OSError:
                errors += 1

    print("Removed {0:d} files/dirs, freed {1:d} bytes, {2:d} errors".format(
          count, size, errors))
