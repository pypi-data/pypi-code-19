#!/usr/bin/python3
import argparse
import sys
import math
import multiprocessing
import threading
import logging
import datetime
import os

from flickrsync import general
from flickrsync import local
from flickrsync.settings import Settings
from flickrsync.database import Database
from flickrsync.flickr import Flickr
from flickrsync.log import Log
from flickrsync.helpaction import _HelpAction

logger = logging.getLogger(Log.NAME)

COMMIT_SIZE = 50
THREAD_COUNT_TAGS = 10
PHOTOSET_MISSING = 'FlickrSync: pictures not on local'

def delete_tables(database, noprompt=False):
    if noprompt or general.query_yes_no('Delete the database?', default='no'):
        database.drop_local_photos_table()
        database.drop_flickr_photos_table()
        database.create_local_photos_table()
        database.create_flickr_photos_table()

def _commit_photos(database, photos):
    database.insert_local_photos(photos)
    database.do_commit()
    logger.info('Added <%d> new photos' % len(photos))

def _search_local(database, directory):
    allfiles = database.select_all_local_photos()
    deletedfiles = local.search_deleted(allfiles)

    if deletedfiles :
        database.update_deleted_photos(deletedfiles)
    else:
        logger.info('No deleted / undeleted photos found')

    newsearch = local.search_photos(directory)

    if newsearch:
        newfiles = database.get_new_files(newsearch)

        if newfiles :
            logger.info('New files found <%s>' % len(newfiles))

            with multiprocessing.Pool() as pool:

                # not able to use the sqlite.row_factory type with map
                # convert to tuple list
                it = pool.imap_unordered(local.image_worker, general.tuple_list_from_rows(newfiles))

                photos = []
                for photo in it:

                    photos.append(photo)

                    if len(photos) >= COMMIT_SIZE:
                        _commit_photos(database, photos)
                        photos.clear()

                _commit_photos(database, photos)
        else:
            logger.info('No new files found')

    else:
        logger.warning('No files found in this directory <%s>' % directory)

def _get_flickr_photosets(database, flickr):
    photosets = flickr.get_photosets()

    database.create_flickr_photosets_table()

    if photosets :
        database.insert_flickr_photosets(photosets)

    else:
        logger.info('No flickr photoSets found')

    return photosets

def create_photosets(database, flickr, rootpath, noprompt=False):
    photosets = _get_flickr_photosets(database, flickr)
    directories = database.get_directories_from_local()

    if len(directories):
        if noprompt or general.query_yes_no('Potentially create / delete <%s> photosets on Flickr?' % len(directories)):
            photosetsused = []

            for directory in directories:
                photos = general.list_from_rows(database.select_flickr_photos_matching_local_by_directory(directory))

                if photos:
                    photosetname = general.get_photoset_name(directory, rootpath)
                    photoscsv = general.list_to_csv(photos)

                    primaryphotoid = photos[0]
                    photosetid = database.get_photoset_id(photosetname)

                    if photosetid:
                        logger.info('Photoset already exists on Flickr <%s>' % photosetname)
                    else:
                        photosetid = flickr.photoset_create(photosetname, primaryphotoid)

                    assert photosetid, 'photosetId is Null'

                    # replace photos in set
                    flickr.photoset_edit(photosetid, primaryphotoid, photoscsv)
                    photosetsused.append(str(photosetid))

                else:
                    logger.warning('No photos found on Flickr match local photos found in <%s>' % directory)

            if photosetsused:
                flickr.delete_unused_photosets(photosetsused = photosetsused, photosets = photosets)
            else:
                logger.warning('no photosets in use')
    else:
        logger.info('No local photo directories found')

def _search_flickr(database, flickr, minuploaddate=-1):
    minuploaddate = minuploaddate if minuploaddate>=0 else (database.select_last_upload_date() + 1)
    humandate = datetime.datetime.fromtimestamp(minuploaddate).strftime(general.FLICKR_DATE_FMT)

    logger.info('Searching Flickr since the last upload date <%s>. This could take a long time' % humandate)

    photos = flickr.get_photos(minuploaddate)

    if photos :
        logger.info('Found new photos on Flickr <%d>' % len(photos))
        database.insert_flickr_photos(photos)
    else:
        humandate = datetime.datetime.fromtimestamp(minuploaddate).strftime(general.FLICKR_DATE_FMT)
        logger.info('No new photos found on Flickr since the last upload date')

def rebase_flickr(database, flickr, noprompt=False):
    if noprompt or general.query_yes_no('Rebase the Flickr database?', default='no'):
        database.drop_flickr_photos_table()
        database.create_flickr_photos_table()
        _search_flickr(database, flickr, minuploaddate=0)

def _do_upload(database, flickr, directory, dryrun=True, noprompt=False):
    uploadphotos = database.select_photos_for_upload()

    logger.info('Selected <%d> photos for upload to Flickr' % len(uploadphotos))

    passed = 0
    failed = 0

    if dryrun:
        logger.info('Dry run, not uploading')
    else:
        if uploadphotos:
            if noprompt or general.query_yes_no('Upload <%d> pictures to Flickr?' % len(uploadphotos)):
                passed, failed = flickr.upload_photos(uploadphotos)

                if passed > 0:
                    _search_flickr(database, flickr)
        else:
            logger.info('No photos to upload')

    logger.info('Uploaded: passed<%d>, failed<%d>' % (passed, failed))
    return passed

def _download_missing_photos_from_flickr(database, directory, dryrun=True, noprompt=False):
    flickrphotos = database.select_missing_flickr_photos()

    if flickrphotos:
        if noprompt or general.query_yes_no('Do you want to download <%d> missing photos from Flickr' % len(flickrphotos)):
            local.download_photos(directory=directory, flickrphotos=flickrphotos, dryrun=dryrun)
            _search_local(database, directory)
    else:
        logger.info('No missing photos to download')

def create_photoset_missing_photos_on_local(database, flickr):
    flickrphotos = database.select_missing_flickr_photos()

    if flickrphotos:
        idlist = []
        for row in flickrphotos:
            idlist.append(row['id'])

        photoscsv = general.list_to_csv(idlist)
        photosetname = '{name} {date}'.format(name=PHOTOSET_MISSING, date=datetime.datetime.now().strftime(general.FLICKR_DATE_FMT))
        primaryphotoid = flickrphotos[0]['Id']
        photosetid = flickr.photoset_create(photosetname, primaryphotoid)

        assert photosetid, 'photosetId is Null'

        flickr.photoset_edit(photosetid, primaryphotoid, photoscsv)

    else:
        logger.info('No missing photos on local')

def _add_tags_worker(flickr, data):
    for photoid, signature in data:
        flickr.add_tags(photoid, signature)

def _add_tags(flickr, localphotos, dryrun=True):
    logger.info('Adding tags to <{count}> Flickr photos'.format(count=len(localphotos)))

    if dryrun:
        logger.info('Dry run, not adding tags')
    else:
        data = []

        for localphoto in localphotos:
            data.append((localphoto['flickrid'], Flickr.get_signature_tag(localphoto['signature'])))

        chunksize = math.ceil(len(data)/THREAD_COUNT_TAGS)

        logger.debug('data<%d>, chunksize<%d>' % (len(data), chunksize))
        assert chunksize, 'Chunksize'

        threads = []
        for chunk in general.chunks(data, chunksize):
            thread = threading.Thread(target=_add_tags_worker, args=(flickr, chunk,))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

def _set_tags_worker(flickr, data):
    for photoid, signature in data:
        flickr.set_tags(photoid, signature)

def delete_tags(database, flickr, stringmatch, dryrun=True, noprompt=False):
    assert stringmatch, 'stringmatch not supplied'
    flickrphotos = database.select_all_flickr_photos_matching_tag(stringmatch)
    logger.info('Deleting tags containing STRING<{stringmatch}> from <{count}> Flickr photos'.format(count=len(flickrphotos), stringmatch=stringmatch))

    if flickrphotos:
        if noprompt or general.query_yes_no('Deleting tags containing STRING<{stringmatch}> from <{count}> Flickr photos'.format(count=len(flickrphotos), stringmatch=stringmatch)):
            data = []
            for flickrphoto in flickrphotos:

                newtags = general.remove_tag_from_tags(flickrphoto['tags'], stringmatch)

                data.append((flickrphoto['id'], newtags))

            chunksize = math.ceil(len(data)/THREAD_COUNT_TAGS)

            logger.debug('data<%d>, chunksize<%d>' % (len(data), chunksize))
            assert chunksize, 'Chunksize'

            if dryrun:
                logger.info('Dry run, not deleting tags')
            else:
                threads = []
                for chunk in general.chunks(data, chunksize):
                    thread = threading.Thread(target=_set_tags_worker, args=(flickr, chunk,))
                    threads.append(thread)

                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()

                _search_flickr(database, flickr, minuploaddate=0)
    else:
        logger.info('No matching Flickr tags found')

def _tag_matched_flickr_photos(database, flickr, directory, dryrun=True, noprompt=False):
    localphotos = database.select_unmatched_photos_with_flickr_id()

    success = False

    if localphotos:
        if noprompt or general.query_yes_no('Do you want to tag <%d> matched pictures found on Flickr' % len(localphotos)):
            try:
                _add_tags(flickr, localphotos, dryrun=dryrun)

            finally:
                minuploaddate = database.select_min_upload_date_without_signature()
                _search_flickr(database, flickr, minuploaddate=minuploaddate)
                success = True

    else:
        logger.info('No matched Flickr photos found')
        success = True

    logger.debug('success <{success}>'.format(success=success))
    return success

def _download_and_scan_unmatched_flickr_photos(database, directory, dryrun=True, noprompt=False, nodatematch=False):
    flickrphotos = database.select_unmatchable_flickr_photos(nodatematch)

    success = False

    if flickrphotos:
        if noprompt or general.query_yes_no('Do you want to download and scan <%d> unmatched pictures from Flickr' % len(flickrphotos)):

            downloaddirectory = os.path.join(directory, general.APPLICATION_NAME)
            local.download_photos(directory=downloaddirectory, flickrphotos=flickrphotos, dryrun=dryrun)
            _search_local(database, downloaddirectory)

            success = True

    else:
        logger.info('No unmatched Flickr photos found')
        success = True

    logger.debug('success <{success}>'.format(success=success))
    return success

def do_sync(database, flickr, directory, twoway=False, dryrun=True, noprompt=False, nodatematch=False, identifymissing=False):
    if noprompt or general.query_yes_no('Do you want to sync the local file system with Flickr'):
        threads = []

        minuploaddate = 0 if identifymissing else -1

        thread = threading.Thread(target=_search_flickr, args=(database, flickr, minuploaddate,))
        threads.append(thread)

        thread = threading.Thread(target=_search_local, args=(database, directory,))
        threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        if _download_and_scan_unmatched_flickr_photos(database, directory, dryrun=dryrun, noprompt=noprompt, nodatematch=nodatematch):
            if _tag_matched_flickr_photos(database, flickr, directory, dryrun=dryrun, noprompt=noprompt):
                _do_upload(database, flickr, directory, dryrun=dryrun, noprompt=noprompt)

                if identifymissing:
                    create_photoset_missing_photos_on_local(database, flickr)

                elif twoway:
                    _download_missing_photos_from_flickr(database, directory, dryrun=dryrun, noprompt=noprompt)

def print_usage(parser, settings):
    parser.print_usage()
    print()
    print('Config file location <%s>' % settings.configname)
    sys.exit(0)

def main():
    try:
        logger.debug('started')
        logger.debug('sys.argv<%s>' % str(sys.argv))

        parser = argparse.ArgumentParser(description = 'A command line tool to backup local file system pictures to Flickr', add_help=False)
        parser.add_argument('-h', '--help', action=_HelpAction, help = 'show this help message and exit')
        parser.add_argument('-c', '--config', type = str, help = 'config file location')
        parser.add_argument('-p', '--profile', type = str, help = 'config profile section')
        parser.add_argument('-u', '--username', type = str, help = 'config Flickr username, overrides the config file')
        parser.add_argument('-d', '--database', type = str, help = 'FlickrSync database location, overrides the config file')
        parser.add_argument('-l', '--directory', type = str, help = 'local picture directory, overrides the config file')
        parser.add_argument('--noprompt', help = 'do not prompt', action = 'store_true')
        parser.add_argument('--debug', help = 'enable debug logging', action = 'store_true')

        subparsers = parser.add_subparsers(dest='actionname')

        parser_auth = subparsers.add_parser('auth', help = 'authenticate with Flickr', add_help=False)

        parser_sync = subparsers.add_parser('sync', help = 'perform a one way sync from the local file system to Flickr', add_help=False)
        parser_sync.add_argument('--nodatematch', help = 'during sync, do not use dates to match', action = 'store_true')
        parser_sync.add_argument('--dryrun', help = 'do not actually upload/download, perform a dry run', action = 'store_true')
        parser_sync.add_argument('--identifymissing', help = 'during sync, create a Flickr photoset of photos missing on local', action = 'store_true')

        parser_sync2 = subparsers.add_parser('sync2', help = 'perform a two way sync between the local file system and Flickr', add_help=False)
        parser_sync2.add_argument('--nodatematch', help = 'during sync, do not use dates to match', action = 'store_true')
        parser_sync2.add_argument('--dryrun', help = 'do not actually upload/download, perform a dry run', action = 'store_true')

        parser_photosets = subparsers.add_parser('photosets', help = 'create Flickr photosets based upon the local file system', add_help=False)

        parser_deletetags = subparsers.add_parser('deletetags', help = 'delete all tags containing STRING', add_help=False)
        parser_deletetags.add_argument('STRING', type = str)
        parser_deletetags.add_argument('--dryrun', help = 'do not actually deleted Flickr tags, perform a dry run', action = 'store_true')

        parser_delete = subparsers.add_parser('delete', help = 'delete the database tables', add_help=False)
        parser_rebase = subparsers.add_parser('rebase', help = 'rebase the Flickr database table', add_help=False)

        args = parser.parse_args()

        if args.debug:
            Log.set_level(logging.DEBUG)
        else:
            Log.set_level(logging.INFO)

        settings = Settings(args)

        if len(sys.argv) < 2:
            print_usage(parser, settings)

        database = Database(settings.database)
        flickr = Flickr(settings.api_key, settings.api_secret, settings.username)

        if args.actionname == 'sync':
            do_sync(database, flickr, settings.directory, twoway=False, dryrun=args.dryrun, noprompt=args.noprompt,
                    nodatematch=args.nodatematch, identifymissing=args.identifymissing)

        elif args.actionname == 'sync2':
            do_sync(database, flickr, settings.directory, twoway=True, dryrun=args.dryrun, noprompt=args.noprompt, nodatematch=args.nodatematch)

        elif args.actionname == 'delete':
            delete_tables(database, noprompt=args.noprompt)

        elif args.actionname == 'photosets':
            create_photosets(database, flickr, settings.directory, noprompt=args.noprompt)

        elif args.actionname == 'deletetags':
            delete_tags(database, flickr, stringmatch=args.STRING, dryrun=args.dryrun, noprompt=args.noprompt)

        elif args.actionname == 'auth':
            flickr.authenticate()

        elif args.actionname == 'rebase':
            rebase_flickr(database, flickr, noprompt=args.noprompt)

        else:
            print_usage(parser, settings)

        database.con.close()

    except AssertionError as e:
        msg = 'AssertionError: %s' % e
        logger.error(msg)

    except Exception as e:
        Log.traceback(logger, e)
        logger.error(e)

    finally:
        print('finished')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        msg = 'Last Error: %s' % e
        print(msg)
