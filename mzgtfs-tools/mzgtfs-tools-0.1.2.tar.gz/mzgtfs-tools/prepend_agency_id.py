#!/usr/bin/python
"""Prepend agency ID to all routes, trips and stops in a GTFS
"""

import mzgtfs.feed
import mzgtfs.util
import sys, os

gtfs_file = sys.argv[1]
if len(sys.argv) > 1:
    replacement_agency_id = sys.argv[2]

gtfs_feed = mzgtfs.feed.Feed(filename=gtfs_file)
gtfs_feed.preload()
files = ["routes.txt", "trips.txt", "stops.txt"]

agency_id = gtfs_feed.agencies()[0].id()

if replacement_agency_id:
    agency_id = replacement_agency_id 

for stop in gtfs_feed.stops():
    new_stop_id = agency_id + '_' + stop.id()
    stop.set('stop_id',new_stop_id)

for route in gtfs_feed.routes():
    new_route_id = agency_id + '_' + route.id()
    route.set('route_id',new_route_id)

for trip in gtfs_feed.trips():
    new_route_id = agency_id + '_' + trip.get('route_id')
    trip.set('route_id',new_route_id)

for f in files:
    if os.path.exists(f):
        os.remove(f)

gtfs_feed.write('routes.txt', gtfs_feed.routes())
gtfs_feed.write('trips.txt', gtfs_feed.trips())
gtfs_feed.write('stops.txt', gtfs_feed.stops())

gtfs_feed.make_zip(gtfs_file + ".new", files=files, clone=gtfs_file)