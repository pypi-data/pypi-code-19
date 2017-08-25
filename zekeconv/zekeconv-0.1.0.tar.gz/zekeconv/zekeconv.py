#!/bin/env python
from __future__ import print_function

import argparse
import traceback
import sys

from . import io
from . import utl

def main():
    parser = argparse.ArgumentParser(description="convert between zeke dump files and directory structures")
    parser.add_argument("-f", "--file",    metavar="DUMP", help="zeke dumk (.zk) file", required=True)
    parser.add_argument("-s", "--source",  metavar="SOURCE", help="origininal source (subroot) of zookeeper tree")
    parser.add_argument("-V", "--verbose", action='store_true', default=False, help="be more verbose")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u",  "--unpack",  metavar="DIR",  help="unpack zeke dump into directory structure")
    group.add_argument("-p",  "--pack",    metavar="DIR",  help="pack directory structure to zeke dump")

    args = parser.parse_args()
    
    # global exception handler
    try:
        source = utl.preprocess_source_subpath(args.source)
        
        # parser ensures these two are mutually exclusive
        if args.unpack:
            if (args.verbose):
                print("unpacking zeke dump '{1}' "
                      "into directory structure at '{0}'".format(args.unpack,
                                                                 args.file),
                      file=sys.stderr)
            io.unpack(args.file, args.unpack, source)
            
        if args.pack:
            if (args.verbose):
                print("packing directory structure at '{0}' "
                      "into zeke dump '{1}'".format(args.pack, args.file),
                      file=sys.stderr)
            io.pack(args.pack, args.file, source)
            
    except Exception as e:
        print("Error ({0}): {1}".format(type(e).__name__, e), file=sys.stderr)
        if args.verbose:
            print(traceback.format_exc(), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
