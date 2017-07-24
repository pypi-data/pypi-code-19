#!/usr/bin/python
"""
Split one route into multiple routes based upon headsign.

Takes a json file as input, with routes to split up, and any new routes to be added:

{ "routes" : [
    {"original_route_id": "route_id",
    "splits":
        {"trip_headsign (exact)": "new route_id" }
    }

]
, "new_routes" : [
    {
        "route_id" : ... ,
        "route_short_name" : ... ,
        "route_long_name" : ... ,
        "route_type" : ... ,
        "route_color" : ... ,
        "route_text_color" : ...,
        "agency_id" : ...
    }
]
}
"""
import json
import pprint
import shutil
import mzgtfs.feed
import plac
import util



def add_route(feed, routeInfo):
    """ add route specified in routeDict to feed"""
    print "adding route " + routeInfo['route_id']
    route_factory = feed.FACTORIES['routes']
    route = route_factory.from_row(routeInfo)
    feed.by_id['routes'][routeInfo['route_id']] = route

def split_route(feed, routeSplitInfo):
    """ take in routes object, modify entities"""
    route_id = routeSplitInfo['original_route_id']
    splits = routeSplitInfo['splits']

    counts = dict.fromkeys(splits, 0)

    for t in feed.route(route_id).trips():
        headsign = t['trip_headsign']
        if headsign in splits:
            new_route_id = splits[headsign]
            t.set('route_id', new_route_id)
            counts[headsign] += 1

    print "updated on route " + route_id
    pprint.pprint(counts)

def main(gtfs_file, input_json_file):
    """ load gtfs_file and instructions from JSON"""
    gtfs_feed = mzgtfs.feed.Feed(filename=gtfs_file)
    gtfs_feed.preload()

    with open(input_json_file) as jsonfile:
        input_json = json.load(jsonfile)

    for new_route in input_json['new_routes']:
        add_route(gtfs_feed, new_route)

    for route in input_json['routes']:
        split_route(gtfs_feed, route)

    files = ["routes.txt", "trips.txt"]

    gtfs_feed.write('routes.txt', gtfs_feed.routes())
    gtfs_feed.write('trips.txt', gtfs_feed.trips())
    
    print "saving file"
    
    gtfs_feed.make_zip('output.zip', files=files, clone=gtfs_file)
    shutil.move('output.zip', gtfs_file)
    util.delete_temp_files(files)


if __name__ == "__main__":
   import plac
   plac.call(main)