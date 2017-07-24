#!/usr/bin/python
"""Add a feed_info with feed_id to the gtfs
usage: add_feed_id.py gtfs_file <optional replacement feed_id> <boolean to replace agency_id with new feed_id>"""

import sys, os, shutil
import mzgtfs.feed
import mzgtfs.util
import util

def rename_agency(gtfs_feed, gtfs_file, original_agency, new_agency, feed_id):
    files = ["feed_info.txt", "agency.txt", "routes.txt"]
    util.delete_temp_files(files)

    aid = None
    for agency in gtfs_feed.agencies():
        if agency.id() == original_agency:
            aid = agency
            break
    if aid == None:
        raise ValueError("No agency id of "+original_agency+" found, exiting")
    
    url = gtfs_feed.agency(aid.id()).get('agency_url')
    lang = gtfs_feed.agency(aid.id()).get('agency_lang')

    print "changing agency "+aid.id()+" to "+new_agency+" and adding feed_id " + feed_id +"."
    
    if lang: 
        feed_lang = lang
    else:
        feed_lang = 'en'
    
    #fix the agency.txt file first
    gtfs_feed.agency(original_agency).set('agency_id', new_agency)
    gtfs_feed.write('agency.txt', gtfs_feed.agencies())

    #now fix the routes.txt file
    for r in gtfs_feed.routes():
        if r.get('agency_id') == original_agency:
            r.set('agency_id', new_agency)
    gtfs_feed.write('routes.txt', gtfs_feed.routes()) 

    
    #no feed info there, make a new one
    try:
        len(gtfs_feed.feed_infos())
        skip = False
        newfi = {}
        key = 97
        for f in gtfs_feed.feed_infos():
            if f.get('feed_publisher_name') == new_agency and not skip:
                cls = gtfs_feed.FACTORIES['feed_info']
                info = cls.from_row({
                    'feed_publisher_name' : new_agency,
                    'feed_publisher_url' : url,
                    'feed_lang' : feed_lang,
                    'feed_id' : feed_id
                    })
                newfi[chr(key)] = info
                skip = True
            else:
                cls = gtfs_feed.FACTORIES['feed_info']
                info = cls.from_row({
                    'feed_publisher_name' : f.get('feed_publisher_name'),
                    'feed_publisher_url' : f.get('feed_publisher_url'),
                    'feed_lang' : f.get('feed_lang'),
                    'feed_id' : f.get('feed_id')
                    })
                newfi[chr(key)] = info
            key = key + 1
        if not skip:
            cls = gtfs_feed.FACTORIES['feed_info']
            info = cls.from_row({
                'feed_publisher_name' : new_agency,
                'feed_publisher_url' : url,
                'feed_lang' : feed_lang,
                'feed_id' : feed_id
                })
            gtfs_feed.by_id['feed_info']['a'] = info
            gtfs_feed.write('feed_info.txt', gtfs_feed.feed_infos())
        else:
            gtfs_feed.by_id['feed_info'] = newfi
            gtfs_feed.write('feed_info.txt', gtfs_feed.feed_infos())
                       
    except Exception as e:
        gtfs_feed.by_id['feed_info'] = {}
        cls = gtfs_feed.FACTORIES['feed_info']
        info = cls.from_row({
            'feed_publisher_name' : new_agency,
            'feed_publisher_url' : url,
            'feed_lang' : feed_lang,
            'feed_id' : feed_id
            })
        gtfs_feed.by_id['feed_info']['a'] = info
        gtfs_feed.write('feed_info.txt', gtfs_feed.feed_infos())
    
    gtfs_feed.make_zip('output.zip', files=files, clone=gtfs_file)
    shutil.move('output.zip', gtfs_file)
    util.delete_temp_files(files)
    

def main(argv):
    if len(argv) < 5:
        print "usage: rename_agency_and_feed.py gtfs_file <original agency id> <new agency id> <feed id for agency>"
        sys.exit(0)
    
    gtfs_file = argv[1]
    original_agency = argv[2]
    new_agency = argv[3]
    feed_id = argv[4]

    gtfs_feed = mzgtfs.feed.Feed(filename=gtfs_file)
    
    try:
        rename_agency(gtfs_feed, gtfs_file, original_agency, new_agency, feed_id)

    except Exception as e:
        print(repr(e))


if __name__ == "__main__":
   main(sys.argv)
