#! /usr/bin/python
"""
make all stops and trips in a feed accessible
"""

import shutil
import mzgtfs.feed
import util

def main(gtfs_file):
    gtfs_feed = mzgtfs.feed.Feed(filename=gtfs_file)

    make_accessible_stops(gtfs_feed)

    make_accessible_trips(gtfs_feed)

    files = ['stops.txt', 'trips.txt']

    cols = ['stop_id','stop_lat','stop_lon','stop_name','wheelchair_boarding']
    gtfs_feed.write('stops.txt', gtfs_feed.stops(), columns=cols)

    cols = ['route_id','trip_id','service_id','direction_id','trip_headsign','shape_id','wheelchair_accessible']
    gtfs_feed.write('trips.txt', gtfs_feed.trips(), columns=cols)

    gtfs_feed.make_zip('output.zip', files=files, clone=gtfs_file)
    shutil.move('output.zip', gtfs_file)

    util.delete_temp_files(files)

def make_accessible_stops(gtfs_feed):
    for stop in gtfs_feed.stops():
        stop.set('wheelchair_boarding', 1)

def make_accessible_trips(gtfs_feed):
    for trip in gtfs_feed.trips():
        trip.set('wheelchair_accessible', 1)



if __name__ == "__main__":
    import plac
    plac.call(main)