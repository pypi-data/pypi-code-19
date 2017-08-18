#!/usr/bin/env python

from __future__ import print_function
# from win32file import CreateFile, SetFileTime, GetFileTime, CloseHandle 

import exifread
import sys, os, re, time, functools
import argparse

def update_timestamp ( fn ):
    TIMESTAMP_TAGS = ["EXIF DateTimeOriginal",
                      "Image DateTime"]
    with open(fn, 'rb') as fh:
        tags = exifread.process_file(fh)
        for TAG in TIMESTAMP_TAGS:
            stamp = tags.get(TAG)
            if stamp:
                break
        else:
            raise Exception("no date tag in {}: {}"
                            .format(fn, tags.keys()))

        t = time.mktime(time.strptime(str(stamp), '%Y:%m:%d %H:%M:%S'))
        os.utime(fn, (t,t))
        print ("updated {} to {}".format(fn, stamp))


def walk_top ( top ):
    print ("walking over '{}'".format(top), file=sys.stderr)
    for (dirpath, dirnames, filenames) in os.walk(top):
        for base in filter(functools.partial(re.match, "(?i).*jpe?g$"),
                           filenames):
            fn = os.path.join(dirpath, base)
            try:
                update_timestamp(fn)
            except Exception as ex:
                print ("ERROR: unable to update {}'s timestamp: {}"
                .format(fn, repr(ex)), file=sys.stderr)
                
def main ():
    parser = argparse.ArgumentParser()
    parser.add_argument("photos-directory",
                        help="top-level directory containing images")
    args = vars(parser.parse_args())
    top = args["photos-directory"]
    walk_top(top)

if __name__ == '__main__':
    main()
