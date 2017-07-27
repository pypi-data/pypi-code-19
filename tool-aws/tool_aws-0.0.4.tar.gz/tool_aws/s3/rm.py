#!/usr/bin/env python

import time
import os
import sys
import boto3
import logging
import multiprocessing
import argparse as ap
from textwrap import dedent
from poolmanager import PoolManager
from botocore.exceptions import ClientError
from tool_aws.s3.utils import S3Keys, getMaxChunkSize

logging.basicConfig(level=logging.INFO)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


def usage():
    logger.info('usage:\n%s [options]\n') % (os.path.basename(sys.argv[0]))
    logger.info('try -h or --help for extended help')


def createParser():
    parser = ap.ArgumentParser(
        description=dedent("""\
        Purpose:
            This script is intended for efficient and MASSIVE RECURSIVE
            DELETION of S3 'folders'. This mean that any resource matching with
            the PREFIX variable, will be DELETED IRREVERSIVELY.

            Use this script CAREFULLY.
            """),
        epilog=dedent("""\
        Disclaimer:
            This software is provided \"as is\" and
            is not granted to work in particular cases or without bugs.
            The author disclaims any responsability in case of data loss,
            computer damage or any other bad issue that could arise
            using this software.
            """),
        formatter_class=ap.RawDescriptionHelpFormatter)

    mandatory = parser.add_argument_group('Mandatory arguments')
    mandatory.add_argument(
        '--profile',
        dest='profileName',
        action='store',
        type=str,
        help='AWS profile',
        required=True)
    mandatory.add_argument(
        '--bucket-name',
        dest='bucketName',
        action='store',
        type=str,
        help='bucket name',
        required=True)
    mandatory.add_argument(
        '--prefix',
        dest='prefix',
        action='store',
        type=str,
        help='Prefix (string) relative to the bucket base path. ',
        required=True)

    optionGroup = parser.add_argument_group('Program options')
    optionGroup.add_argument(
        '-n', '--threads-number',
        dest='nbThreads',
        action='store',
        type=int,
        default=None,
        help='Number of threads (subprocess), default: machine number of CPUs')
    optionGroup.add_argument(
        '-s', '--chunk-size',
        dest='chunkSize',
        action='store',
        type=int,
        default=None,
        help='Chunk size for S3 batch deletion, \
            default is set to 1000 (maximal value for S3)')
    optionGroup.add_argument(
        '-f', '--force',
        dest='force',
        action='store_true',
        default=False,
        help='force the removal, i.e. no prompt for confirmation.')

    return parser


def parseArguments(parser, argv):
    options = parser.parse_args(argv[1:])

    profileName = options.profileName
    bucketName = options.bucketName
    prefix = options.prefix
    # Support * operator
    if prefix.endswith('/*'):
        prefix = prefix[:len(prefix) - 1]
    nbThreads = options.nbThreads or multiprocessing.cpu_count()
    chunkSize = options.chunkSize
    force = options.force
    return profileName, bucketName, prefix, chunkSize, nbThreads, force


def callback(counter, response):
    if response:
        logger.info('number of requests per batch: %s' % counter)
        logger.info('result: %s' % response)


def startJob(keys, force):
    if len(keys) == 0:
        logger.info('Actually, there\'s nothing to do... aborting')
        logger.info('Hint: if your prefix starts with \'/\'')
        logger.info('simply remove the first character.')
        return False

    # There is no way to count all keys without listing them all first.
    # We want to avoid listing them all several times,
    # so we only provide the size of the first batch.
    if keys.chunkSize == keys.maxKeys:
        logger.info('There are more than %s keys in total.\n' +
                    'These represents the first batch.' % keys.chunkSize)
    logger.info('Warning: the script will now start deleting:')
    logger.info(keys)

    if force:
        return True

    while True:
        userInput = raw_input(
            'Are you sure you want to continue (there is no way back)? y/n:')
        userInput = userInput.lower()
        if userInput not in (u'y', u'n'):
            logger.info('Error: unrecognized option \'%s\'' % userInput)
            logger.info('Please provide a valid input character...')
            continue
        else:
            break

    if userInput == u'n':
        logger.info('You have refused to proceed, the script will now abort.')
        return False
    return True


def deleteKeys(keys):
    # When using SSL and multithreading one need to create one connection
    # per process. See also: http://stackoverflow.com/questions/
    # 3724900/python-ssl-problem-with-multiprocessing
    session = boto3.session.Session(profile_name=profileName)
    s3 = session.resource('s3')
    S3Bucket = s3.Bucket(bucketName)
    try:
        response = S3Bucket.delete_objects(Delete=keys)
    except ClientError as e:
        if e.response['Error']['Code'] == 'SlowDown':
            logger.info('We are going to fast for S3 it seems.')
            logger.info('Pausing for 5 sec...')
            time.sleep(5)
            return deleteKeys(keys)
        raise Exception(str(e))
    except Exception as e:
        raise Exception(str(e))
    return response


def main():
    global bucketName, profileName
    pm = None
    parser = createParser()
    profileName, bucketName, prefix, chunkSize, nbThreads, force = \
        parseArguments(parser, sys.argv)

    # Maximum number of keys to be listed at a time
    session = boto3.session.Session(profile_name=profileName)
    s3 = session.resource('s3')
    S3Bucket = s3.Bucket(bucketName)
    keys = S3Keys(S3Bucket, prefix)
    chunkSize = chunkSize or getMaxChunkSize(nbThreads, len(keys))
    keys.chunk(chunkSize)
    if startJob(keys, force):
        logger.info('Deletion started...')
        # Make sure we delete the first batch
        previousNumberOfKeys = keys.maxKeys
        while len(keys) > 0 and previousNumberOfKeys == keys.maxKeys:
            if pm:
                keys = S3Keys(S3Bucket, prefix)
                keys.chunk(chunkSize)
                if len(keys):
                    logger.info('New batch delete')
                    logger.info(str(keys))
            if len(keys):
                pm = PoolManager(numProcs=nbThreads)
                pm.imap_unordered(
                    deleteKeys,
                    keys,
                    keys.chunkSize,
                    callback=callback)
            previousNumberOfKeys = len(keys)
    logger.info('Deletion finished...')


if __name__ == '__main__':
    main()
