"""remove an agency from GTFS if no routes are present that use that agency
"""
import sys, os, shutil
import mzgtfs.feed
import mzgtfs.util
import util


def main(argv):
    if len(argv) < 2:
        print "usage: simple_agency_remove.py gtfs_file"
        sys.exit(0)

    files = ['agency.txt']

    gtfs_file = argv[1]

    f = mzgtfs.feed.Feed(gtfs_file)
    
    agencies_in_routes = set((r.get('agency_id') for r in f.routes()))

    for a in f.agencies():
        if a.id() not in agencies_in_routes:
          f.by_id['agency'].pop(a.id())

    f.write('agency.txt', f.agencies())
    f.make_zip('output.zip', files=files, clone=gtfs_file)
    shutil.move('output.zip', gtfs_file)
    util.delete_temp_files(files)
    
if __name__ == "__main__":
   main(sys.argv)