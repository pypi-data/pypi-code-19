#!/usr/bin/env python3
"""Utility for uploading Jekyll site files to an S3 bucket."""

import hashlib
import mimetypes
import logging
import logging.config
import os
import urllib.request
import sys

import boto3
import yaml


def sync_bucket(
        bucket, mime_types, site_root, charset, strip_html, delete_old):
    """Synchronize bucket with the contents of site_root.
    Files are uploaded when not present in the bucket. Files are only uploaded
    if file and object ETags don't match. File Content-Type will be guessed by
    file extension using mime_types. File Content-Type charset will be assigned
    to "text" subtype files. Files ending with ".html" will be uploaded without
    extension if strip_html is True. Files in the bucket that do not exist in
    the local directory will be deleted if delete_old is True.

    Raise ValueError if a file's Content-Type can't be resolved.
    Raise botocore.exceptions.BotoCoreError if a Boto error occurs.
    Raise botocore.exceptions.ClientError if an S3 error occurs.
    """
    logger = logging.getLogger(__name__)
    logger.info('Synchronizing bucket "%s"...', bucket.name)

    object_map = {
        obj.key: obj.e_tag
        for obj in bucket.objects.all()
    }  # key -> e_tag

    file_paths = list(walk_file_paths(os.walk(site_root)))
    file_map = {
        make_key(site_root, path, strip_html): path
        for path in file_paths
    }  # key -> file_path

    logger.info("Uploading new objects...")
    file_map_items = sorted(file_map.items(), key=lambda item: item[1])  # path
    for key, file_path in file_map_items:
        with open(file_path, 'rb') as file:
            # upload if the file ETag doesn't match the object ETag
            if calc_e_tag(file) != object_map.get(key):
                content_type = guess_content_type(
                    file_path, mime_types, charset)
                logger.info(" + %s -> %s, %s", file_path, key, content_type)
                file.seek(0)  # reset file
                bucket.put_object(Key=key, ContentType=content_type, Body=file)

    if delete_old:
        logger.info("Deleting old objects...")
        old_keys = object_map.keys() - file_map.keys()
        for key in sorted(old_keys):
            logger.info(" - %s", key)
        if old_keys:
            bucket.delete_objects(
                Delete={
                    'Objects': [
                        {'Key': key} for key in old_keys
                    ]
                })

    logger.info("Synchronization complete.")


def walk_file_paths(walk_generator):
    """Iterate a walk generator and yield file paths."""
    for root, dirs, filenames in walk_generator:
        for filename in filenames:
            yield os.path.join(root, filename)


def make_key(site_root, file_path, strip_html):
    """Make a bucket key from file_path relative to site_root.
    If strip_html is True ".html" suffix will be removed.
    """
    rel_path = os.path.relpath(file_path, site_root)
    if strip_html and file_path.endswith('.html'):
        rel_path = rel_path[:-len('.html')]
    return urllib.request.pathname2url(rel_path)


def guess_content_type(file_path, mime_types, charset):
    """Guess the content type of a file based on filename.
    Charset will be assigned to a mime subtype of "text".

    Raise ValueError if the mime type of a file cannot be determined.
    """
    content_type, encoding = mime_types.guess_type(file_path)
    if content_type is None:
        raise ValueError('Could not find mime type for "%s"' % file_path)
    if content_type.startswith('text/'):
        content_type += '; charset=' + charset
    return content_type


def calc_e_tag(file):
    """Calculate an S3 ETag from the contents of a file.
    An S3 ETag is a double quoted MD5 hash of file contents.
    """
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: file.read(4096), b''):
        hash_md5.update(chunk)
    return '"%s"' % hash_md5.hexdigest()


def load_config(path):
    """Load configuration from a YAML file.

    Raise FileNotFoundError if path does not exist.
    Raise yaml.YAMLError if YAML file is invalid.
    Raise ValueError if YAML file does not contain a root object.
    Raise ValueError if YAML file is missing bucket value.
    """
    with open(path, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
        validate_config(config)
        return config


def validate_config(config):
    """Validate the structure and required keys of a config dict.

    Raise ValueError if YAML file does not contain a root object.
    Raise ValueError if YAML file is missing bucket value.
    """
    # validate basic structure
    if not isinstance(config, dict):
        raise ValueError("YAML root must be an object.")
    # validate required values
    if 'bucket' not in config:
        raise ValueError('Required "bucket" value is missing.')


def main():
    """Standalone script entry-point."""
    # silence boto unless something _really_ bad happens
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    logging.getLogger('boto3').setLevel(logging.CRITICAL)

    # set up logging for human consumption
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger(__name__)

    try:
        config = load_config('_upload.yml')
        bucket = boto3.resource('s3').Bucket(config['bucket'])
        mime_types = mimetypes.MimeTypes()
        mime_types.types_map[1].update(config.get('mime_types', {}))
        sync_bucket(
            bucket, mime_types,
            config.get('site_root', '_site'),
            config.get('charset', 'utf-8'),
            config.get('strip_html', False),
            config.get('delete_old', False))
    except Exception as error:
        logger.error("Error: %s", error)
        return 1


if __name__ == '__main__':
    sys.exit(main())
