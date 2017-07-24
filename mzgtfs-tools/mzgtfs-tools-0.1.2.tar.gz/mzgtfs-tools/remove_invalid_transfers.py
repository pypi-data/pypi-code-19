#!/usr/bin/python
"""Add a feed_info with feed_id to the gtfs
usage: add_feed_id.py gtfs_file <optional replacement feed_id> <boolean to replace agency_id with new feed_id>"""

import sys, os, shutil
import mzgtfs.feed
import mzgtfs.util
import util


def fix_transfers(gtfs_file, gtfs_feed):
    files = ["transfers.txt"]
    util.delete_temp_files(files)

    xfers = list()
    for t in gtfs_feed.transfers():
        to = t['to_stop_id']
        fr = t['from_stop_id']
        for s in gtfs_feed.stops():
            sid = s['stop_id']
            if sid == to:
                to = "COMPLETEDSTOPID"
            if sid == fr:
                fr = "COMPLETEDSTOPID"
        if to == "COMPLETEDSTOPID" and fr == "COMPLETEDSTOPID":
            xfers.append(t)
        else:
            print("Dropping Xfer to: %s from: %s because the stops weren't found in stops.txt." % (t['to_stop_id'], t['from_stop_id']))

    gtfs_feed.by_id['transfers'] = {}
    cls = gtfs_feed.FACTORIES['transfers']
    i = 0
    gtfs_feed.by_id['transfers'] = {}
    for x in xfers:
        xfer = cls.from_row({
            'from_stop_id' : x['from_stop_id'],
            'to_stop_id' : x['to_stop_id'],
            'transfer_type' : x['transfer_type'],
            'min_transfer_time' : x['min_transfer_time']
            })
        gtfs_feed.by_id['transfers'][i] = xfer
        i = i + 1

    #for t in gtfs_feed.transfers():
    #    print(t['from_stop_id'])

    gtfs_feed.write('transfers.txt', gtfs_feed.transfers())
    gtfs_feed.make_zip('output.zip', files=files, clone=gtfs_file)
    shutil.move('output.zip', gtfs_file)
    util.delete_temp_files(files)

def main(argv):
    if len(argv) < 2:
        print "usage: fix_transfers.py gtfs_file"
        sys.exit(0)

    gtfs_file = argv[1]
    gtfs_feed = mzgtfs.feed.Feed(filename=gtfs_file)

    try:
        fix_transfers(gtfs_file, gtfs_feed)

    except Exception as e:
        print(repr(e))


if __name__ == "__main__":
   main(sys.argv)
