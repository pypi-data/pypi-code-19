#!/usr/bin/python
"""
Replace headsigns based upon shape_id

Takes a json file with a simple dict as input

{ 
    "shape_id" : "new_headsign"
}
"""
import json
import shutil
import mzgtfs.feed
import util

def main(gtfs_file, input_json_file):
    """ load gtfs_file and instructions from JSON"""
    gtfs_feed = mzgtfs.feed.Feed(filename=gtfs_file)
    gtfs_feed.preload()

    with open(input_json_file) as jsonfile:
        input_json = json.load(jsonfile)

    for shape_id, new_headsign in input_json.iteritems():
        printed = False
        print "updating shape " + shape_id + " to " + new_headsign
        
        #set comprehension did not work :/
        for t in gtfs_feed.trips():
            if t.get('shape_id') == shape_id:
                if not printed:
                    print "originally  " + t.get('trip_headsign')
                    print "now  " + new_headsign
                    printed = True
                t.set('trip_headsign', new_headsign)

    gtfs_feed.write('trips.txt', gtfs_feed.trips())
    files = ['trips.txt']

    print "saving file"
    
    gtfs_feed.make_zip('output.zip', files=files, clone=gtfs_file)
    shutil.move('output.zip', gtfs_file)
    util.delete_temp_files(files)


if __name__ == "__main__":
   import plac
   plac.call(main)
