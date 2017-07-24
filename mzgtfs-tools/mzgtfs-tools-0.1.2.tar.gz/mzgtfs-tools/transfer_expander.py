#!/usr/bin/python
"""
"""

import sys, os, shutil
import mzgtfs.feed
import mzgtfs.util
import util

def main(gtfs_file):
    gtfs_feed = mzgtfs.feed.Feed(filename=gtfs_file)

    #preload stops
    # pylint: disable=unused-variable
    stops = gtfs_feed.stops()

    #map parent stations -> children
    parent_stations = defaultdict(set)

    for s in gtfs_feed.iterread('stops'):
        if s.get('parent_station'):
            p = s.get('parent_station').id()
            parent_stations[p].add(s.id())

    xfers = list()
    for t in gtfs_feed.transfers():
        to = t['to_stop_id']
        fr = t['from_stop_id']
        if to == fr:
            all_transfers = util.powerset(parent_stations[to])
            for 





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
        

if __name__ == "__main__":
    import plac
    plac.call(main)