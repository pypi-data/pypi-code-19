#!/usr/bin/python
"""
Create a transfers_human.txt that contains the names of stops, not just their ids.
"""

import mzgtfs.feed
import util

def main(gtfs_file):
    gtfs_feed = mzgtfs.feed.Feed(filename=gtfs_file)

    #preload stops
    # pylint: disable=unused-variable
    stops = gtfs_feed.stops()

    for t in gtfs_feed.transfers():
        from_stop = gtfs_feed.stop(t.get('from_stop_id')).name()
        to_stop = gtfs_feed.stop(t.get('to_stop_id')).name()
        t.set('from_stop', from_stop)
        t.set('to_stop', to_stop)

    cols = ['from_stop', 'to_stop', 'min_transfer_time', 'transfer_type', 'from_stop_id', 'to_stop_id']

    gtfs_feed.write('transfers_human.txt', gtfs_feed.transfers(), columns=cols)

if __name__ == "__main__":
    import plac
    plac.call(main)