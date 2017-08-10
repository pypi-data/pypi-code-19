#!/usr/bin/env python
"""This is the main module of the application."""

# standard library
import argparse
import json
import logging
import multiprocessing.dummy
import os

# third party
import pymongo
import raven

# hoottit
import hoottit.consumers
import hoottit.util
import hoottit.producers


def _get_parser():
    """Create a parser instance and add the necessary arguments.

    This parser will be used to parse arguments supplied by the user. All of
    them have defauls and a self-explanatory description.
    """
    parser = argparse.ArgumentParser(
        description=('Hoottit - Cache subreddits in a MongoDB database for '
                     'later use.'))
    parser.add_argument('-f', '--config',
                        help='specify a custom config file (defaults to '
                        'hoottit.json)',
                        default='hoottit.json',
                        type=str,
                        metavar='PATH')
    parser.add_argument('-c', '--comments',
                        help='stream comments',
                        action='store_true',
                        default=False)
    parser.add_argument('-s', '--submissions',
                        help='stream submissions',
                        action='store_true',
                        default=False)
    parser.add_argument('-t', '--log-threshold',
                        help='output logs to each T documents',
                        default=100,
                        type=int,
                        metavar='T')
    return parser


def _get_config(filepath='hoottit.json'):
    """Load the configuration file.

    This function loads the hoottit configuration from either hoottit.json or
    some other file that the user specified using the -f (--config) option.
    """
    # we intentionally do not catch any exception here
    with open(filepath, 'r') as config_file:
        return json.load(config_file)


def main():
    """This is the main entry point. Here we launch the threads that stream
    submissions and comments to the database
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s @ %(threadName)s -- %(module)s.'
                        '%(funcName)s -- [%(levelname)s] %(message)s')
    if 'HOOT_SENTRYDSN' in os.environ:
        raven.Client(os.environ['HOOT_SENTRYDSN'])
        logging.info('Sentry client initialized.')
    parser = _get_parser()
    args = vars(parser.parse_args())
    config = _get_config(args['config'])
    dburi = 'mongodb://localhost:27017/hoot'
    if 'HOOT_MONGODBURI' in os.environ:
        dburi = os.environ['HOOT_MONGODBURI']
    client = pymongo.MongoClient(dburi)
    databse = client.get_default_database()
    subs = config['subreddits']
    pool = multiprocessing.dummy.Pool(2)
    pool.map(hoottit.util.execute, (
        hoottit.util.pipe(
            getattr(hoottit.producers, p)(subs),
            hoottit.consumers.mongo_upsert(databse[p],
                                           'reddit_id',
                                           args['log_threshold'])
        ) for p in ['comments', 'submissions'] if args[p]))

if __name__ == '__main__':
    main()
