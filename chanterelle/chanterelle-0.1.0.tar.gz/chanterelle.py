#!/usr/bin/env python3
"""Utility for uploading Jekyll site files to an S3 bucket."""

import collections
import hashlib
import mimetypes
import logging
import logging.config
import os
import urllib.request
import sys

import boto3
import botocore.exceptions
import yaml


class Client:
    """Client that synchronizes an S3 bucket with a local static site."""
    CONFIG_PATH = '_upload.yml'

    def __init__(self, site, bucket, delete_old):
        """Create a Client that synchronizes the specified bucket and site.
        Files that are present in the bucket but not in the local site will be
        deleted from the bucket if the delete_old option is True."""
        self._logger = logging.getLogger(__name__)
        self._site = site
        self._bucket = bucket
        self._delete_old = delete_old

    @staticmethod
    def from_config(path=CONFIG_PATH):
        """Create a Client with settings loaded from a config file."""
        config = Config.load(path)
        site = Site(
            config.site_root,
            config.mimetypes,
            config.charset,
            config.strip_html)
        bucket = Bucket.from_name(config.bucket)
        return Client(site, bucket, config.delete_old)

    def sync(self):
        """Synchronize the content of the bucket with the site files.

        Raise SyncError if an error occurs synchronizing the bucket and folder.
        """
        self._logger.info('Synchronizing bucket "%s"...', self._bucket.name)

        try:
            self._logger.info("Uploading new objects...")
            site_files = list(self._site.files()) # must be list to use twice
            e_tag_map = self._bucket.e_tag_map() # s3 key -> e_tag
            for site_file in site_files:
                if site_file.e_tag == e_tag_map.get(site_file.key):
                    # skip upload if local and remote ETags match
                    self._logger.debug(" = %s == %s",
                        site_file.path, site_file.key)
                else:
                    # upload
                    self._logger.info(" + %s -> %s, %s",
                        site_file.path, site_file.key, site_file.content_type)
                    self._bucket.upload(site_file)

            if self._delete_old:
                self._logger.info("Deleting old objects...")
                local_keys = set(sf.key for sf in site_files)
                old_keys = e_tag_map.keys() - local_keys
                for key in old_keys:
                    self._logger.info(" - %s", key)
                if old_keys:
                    self._bucket.delete(old_keys)

        except botocore.exceptions.BotoCoreError as error:
            raise SyncError("Boto error: " + str(error)) from error
        except botocore.exceptions.ClientError as error:
            raise SyncError("S3 error: " + str(error)) from error

        self._logger.info("Synchronization complete.")

class SyncError(Exception):
    """Raised when an error occurs synchronizing a bucket and folder."""
    pass

class Config:
    """Configuration for Client. This class is responsible for loading a
    configuration file and setting defaults for optional values."""
    SITE_ROOT= '_site'
    CHARSET = 'utf-8'

    def __init__(self, config_dict):
        """Create configuration from a dict of values.

        Raise ValueError if the config_dict is missing required values or
        contains invalid values.
        """
        try:
            self.bucket = config_dict['bucket']
        except KeyError as error:
            raise ValueError('Required "bucket" value is missing.') from error

        # load mime-types
        self.mimetypes = mimetypes.MimeTypes()
        mime_types = config_dict.get('mime_types', {})
        self.mimetypes.types_map[1].update(mime_types) # add custom types

        self.site_root = config_dict.get('site_root', Config.SITE_ROOT)
        self.charset = config_dict.get('charset', Config.CHARSET)
        self.strip_html = config_dict.get('strip_html', False)
        self.delete_old = config_dict.get('delete_old', False)

    @staticmethod
    def load(path):
        """Load a configuration from a YAML file. After the configuration is
        loaded the site_root location will be updated to be relative to the
        directory containing the Config file.

        Raise FileNotFoundError if path does not exist.
        Raise ParseError if YAML file is invalid or missing required values.
        """
        with open(path, 'r') as yaml_file:
            try:
                config_dict = yaml.safe_load(yaml_file)
                # validate basic structure
                if not isinstance(config_dict, dict):
                    raise ParseError("YAML root must be an object.")
                config = Config(config_dict)
                # adjust paths to be relative to the config file location
                config_dir = os.path.dirname(path)
                config.site_root = os.path.relpath(
                    config.site_root, config_dir)
                return config
            except yaml.YAMLError as error:
                raise ParseError("File contains invalid YAML.") from error
            except ValueError as error:
                raise ParseError(error) from error

class ParseError(Exception):
    """Raised when there is an error parsing a Config file."""
    pass

class Site:
    """Directory of site files."""

    def __init__(self, site_root, mimetypes, charset, strip_html):
        """Create a Site located at site_root. The mimetypes object will be
        used to resolve the file's content_type based on filename. The charset
        will be assigned to any file of the type "text/*". If strip_html is
        true the key of files with filenames ending in ".html" will be
        extensionless.
        """
        self._site_root = site_root
        self._mimetypes = mimetypes
        self._charset = charset
        self._strip_html = strip_html

    def files(self):
        """Return a list of all SiteFiles under the site root.

        Raise ValueError if the mime type of a file cannot be determined.
        """
        for root, dirs, filenames in os.walk(self._site_root):
            for filename in filenames:
                path = os.path.join(root, filename)
                yield SiteFile(
                    path,
                    self._key(path),
                    self._content_type(path),
                    self._e_tag(path))

    def _key(self, file_path):
        """Create the bucket key for a file from its path."""
        rel_path = os.path.relpath(file_path, self._site_root)
        if self._strip_html and file_path.endswith('.html'):
            rel_path = rel_path[:-len('.html')]
        return urllib.request.pathname2url(rel_path)

    def _content_type(self, file_path):
        """Determine the content type of a file based on filename.

        Raise ValueError if the mime type of a file cannot be determined.
        """
        content_type, encoding = self._mimetypes.guess_type(file_path)
        if content_type is None:
            raise ValueError('Could not find mime type for "%s"' % file_path)
        if content_type.startswith('text/'):
            content_type += '; charset=' + self._charset
        return content_type

    def _e_tag(self, file_path):
        """Generate the S3 ETag of a site file."""
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as site_file:
            for chunk in iter(lambda: site_file.read(4096), b''):
                hash_md5.update(chunk)
        return '"%s"' % hash_md5.hexdigest()

SiteFile = collections.namedtuple(
    'SiteFile',
    ('path', 'key', 'content_type', 'e_tag'))
SiteFile.__doc__ = """Metadata for a site file. The path is the location of the
file. The key is the S3 bucket key. The content_type is the HTTP content type
and optional charset of the file contents. The e_tag is the S3 entity tag that
identifies the file contents.
"""

class Bucket:
    """Simple interface to an S3 bucket. This is a small wrapper around Boto
    that simplifies bucket interactions and enables cleaner testing.
    """

    def __init__(self, boto_bucket):
        """Create a bucket that wraps the boto_bucket."""
        self._logger = logging.getLogger(__name__)
        self._boto_bucket = boto_bucket

    @staticmethod
    def from_name(bucket_name):
        """Create a bucket with a Boto bucket having bucket_name."""
        boto_bucket = boto3.resource('s3').Bucket(bucket_name)
        return Bucket(boto_bucket)

    @property
    def name(self):
        """Name of the S3 bucket."""
        return self._boto_bucket.name

    def e_tag_map(self):
        """Return a map of object key to ETag for all objects in the bucket.

        Raise botocore.exceptions.BotoCoreError if a general error occurs.
        Raise botocore.exceptions.ClientError if an error occurs with S3.
        """
        return {obj.key: obj.e_tag
            for obj in self._boto_bucket.objects.all()}

    def upload(self, site_file):
        """Upload a site file to the bucket.

        Raise botocore.exceptions.BotoCoreError if a general error occurs.
        Raise botocore.exceptions.ClientError if an error occurs with S3.
        """
        with open(site_file.path, 'rb') as object_file:
            self._boto_bucket.put_object(
                Key=site_file.key,
                ContentType=site_file.content_type,
                Body=object_file)

    def delete(self, keys):
        """Delete a collection of keys from the bucket.

        Raise botocore.exceptions.BotoCoreError if a general error occurs.
        Raise botocore.exceptions.ClientError if an error occurs with S3.
        """
        self._boto_bucket.delete_objects(
            Delete={'Objects': [{'Key': key} for key in keys]})


def main():
    """Standalone script entry-point."""
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    logging.getLogger('boto3').setLevel(logging.CRITICAL)
    logger = logging.getLogger(__name__)

    try:
        client = Client.from_config()
        client.sync()
    except (FileNotFoundError, ParseError) as error:
        logger.error("Error loading configuration: %s", error)
        return 1
    except SyncError as error:
        logger.error("Error synchronizing bucket: %s", error)
        return 1
    except Exception:
        logger.error("Unknown error:", exc_info=True)
        return 2


if __name__ == '__main__':
    sys.exit(main())
