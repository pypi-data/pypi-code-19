import os
import tempfile
import re

import sys
import logging

import lore
from lore.util import timer
from lore.io.connection import Connection

if not (sys.version_info.major == 3 and sys.version_info.minor >= 6):
    ModuleNotFoundError = ImportError
try:
    import boto3
    from botocore.exceptions import ClientError
except ModuleNotFoundError as e:
    boto3 = False
    ClientError = Exception

logger = logging.getLogger(__name__)


# TODO abstract this file for open source
# for key in os.environ:
#     match = re.match('(.*)_DATABASE_URL', key)
#     if match:
#         name = match.group(1)
#         __set
ANALYSIS_DATABASE_URL = os.environ.get("ANALYSIS_DATABASE_URL")
if ANALYSIS_DATABASE_URL is not None:
    analysis = Connection(ANALYSIS_DATABASE_URL)

CUSTOMERS_DATABASE_URL = os.environ.get("CUSTOMERS_DATABASE_URL")
if CUSTOMERS_DATABASE_URL is not None:
    customers = Connection(CUSTOMERS_DATABASE_URL)

CATALOG_DATABASE_URL = os.environ.get("CATALOG_DATABASE_URL")
if CATALOG_DATABASE_URL is not None:
    catalog = Connection(CATALOG_DATABASE_URL)

SHOPPERS_DATABASE_URL = os.environ.get("SHOPPERS_DATABASE_URL")
if SHOPPERS_DATABASE_URL is not None:
    shoppers = Connection(SHOPPERS_DATABASE_URL)


if boto3:
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if AWS_ACCESS_KEY_ID is not None and AWS_SECRET_ACCESS_KEY is not None:
        s3 = boto3.resource(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    else:
        s3 = boto3.resource('s3')
    
    bucket = s3.Bucket(os.environ.get('S3_BUCKET', 'shoppers-picking'))


def download(local_path, cache=True):
    remote_path = re.sub(
        r'^%s' % re.escape(lore.env.work_dir),
        lore.env.name,
        local_path
    )
    
    if cache and os.path.exists(local_path):
        return
    
    dir = os.path.dirname(local_path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    with timer('DOWNLOAD: %s -> %s' % (remote_path, local_path)):
        temp_file, temp_path = tempfile.mkstemp()
        try:
            bucket.download_file(remote_path, temp_path)
        except ClientError as e:
            logger.error("Error downloading file: %s" % e)
            raise
        
        os.rename(temp_path, local_path)


def upload(local_path):
    remote_path = re.sub(
        r'^%s' % re.escape(lore.env.work_dir),
        lore.env.name,
        local_path
    )
    
    with timer('UPLOAD: %s -> %s' % (local_path, remote_path)):
        try:
            bucket.upload_file(local_path, remote_path)
        except ClientError as e:
            logger.error("Error uploading file: %s" % e)
            raise
