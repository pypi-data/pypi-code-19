#!/usr/bin/python
"""Add a feed_info with feed_id to the gtfs
usage: add_feed_id.py gtfs_file <optional replacement feed_id> <boolean to replace agency_id with new feed_id>"""

import sys, os, shutil
import mzgtfs.feed
import mzgtfs.util
import util


def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError # evil ValueError that doesn't tell you what the wrong value was

def add_feed_id(gtfs_feed, gtfs_file, feed_id = None, new_agency_id_bool = False):
    files = ["feed_info.txt"]
    util.delete_temp_files(files)

    if len(gtfs_feed.agencies()) > 1 and new_agency_id_bool is True:
        raise ValueError('cannot replace agency_id when there is more than one agency')

    agency_id = gtfs_feed.agencies()[0].id()
    url = gtfs_feed.agency(agency_id).get('agency_url')
    lang = gtfs_feed.agency(agency_id).get('agency_lang')
    feed_id = feed_id or agency_id

    print "adding feed_id " + feed_id +" to " + gtfs_file
        
    if lang:
        feed_lang = lang
    else:
        feed_lang = 'en'

    if str_to_bool(new_agency_id_bool):
        gtfs_feed.agency(agency_id).set('agency_id', feed_id)
        agency_id = feed_id

        files.append('agency.txt')
        files.append('routes.txt')

        gtfs_feed.write('agency.txt', gtfs_feed.agencies())

        for r in gtfs_feed.routes():
            r.set('agency_id', feed_id)
        gtfs_feed.write('routes.txt', gtfs_feed.routes())
    else:
        pass

    if 'feed_info' not in gtfs_feed.by_id:
        gtfs_feed.by_id['feed_info'] = {}
        cls = gtfs_feed.FACTORIES['feed_info']
        info = cls.from_row({
            'feed_publisher_name' : agency_id,
            'feed_publisher_url' : url,
            'feed_lang' : feed_lang,
            'feed_id' : feed_id
            })
        gtfs_feed.by_id['feed_info']['a'] = info

    else:
        gtfs_feed.feed_infos.set('feed_id', feed_id)


    gtfs_feed.write('feed_info.txt', gtfs_feed.feed_infos())
    gtfs_feed.make_zip('output.zip', files=files, clone=gtfs_file)
    shutil.move('output.zip', gtfs_file)
    util.delete_temp_files(files)


def main(argv):
    if len(argv) < 2:
        print "usage: add_feed_id.py gtfs_file <optional replacement feed_id> <boolean to replace agency_id with new feed_id>"
        sys.exit(0)

    feed_id = argv[2] if len(argv) > 2 else None
    new_agency_id_bool = argv[3] if len(argv) >3 else False

    gtfs_file = argv[1]
    gtfs_feed = mzgtfs.feed.Feed(filename=gtfs_file)

    try:
        add_feed_id(gtfs_feed, gtfs_file, feed_id, new_agency_id_bool)

    except Exception as e:
        print repr(e)

if __name__ == "__main__":
   main(sys.argv)
