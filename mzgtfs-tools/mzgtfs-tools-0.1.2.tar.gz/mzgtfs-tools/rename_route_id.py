#!/usr/bin/python
""" update route_id to specified route_id
Usage: rename_route_id.py <original_route_id> <new_route_id>
"""
import sys, os, shutil
import mzgtfs.feed
import mzgtfs.util
import util

def rename_route_id(gtfs_feed, gtfs_file, original_route_id, new_route_id):
    files = ['trips.txt', 'routes.txt']

    util.delete_temp_files(files)

    for t in gtfs_feed.trips():
        if t.get('route_id') == original_route_id:
            t.set('route_id', new_route_id)

    for r in gtfs_feed.routes():
        if r.get('route_id') == original_route_id:
            gtfs_feed.by_id['routes'].pop(original_route_id)

    gtfs_feed.write('trips.txt', gtfs_feed.trips())
    gtfs_feed.write('routes.txt', gtfs_feed.routes())
    gtfs_feed.make_zip('output.zip', files=files, clone=gtfs_file)
    shutil.move('output.zip', gtfs_file)
    util.delete_temp_files(files)


def main(argv):
    if len(argv) < 3:
        print "Usage: rename_route_id.py <original_route_id> <new_route_id>"
        sys.exit(0)

    original_route_id = argv[2]
    new_route_id = argv[3] 

    gtfs_file = argv[1]
    gtfs_feed = mzgtfs.feed.Feed(filename=gtfs_file)
    
    try:
        rename_route_id(gtfs_feed, gtfs_file, original_route_id, new_route_id)

    except Exception as e:
        print(repr(e))


if __name__ == "__main__":
   main(sys.argv)