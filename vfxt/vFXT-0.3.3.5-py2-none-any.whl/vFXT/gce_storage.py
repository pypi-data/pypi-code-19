# Copyright (c) 2015-2016 Avere Systems, Inc.  All Rights Reserved.             
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
import logging
import os
import httplib2
import threading
import Queue
import time
import json

import googleapiclient.discovery
import oauth2client.client
import googleapiclient

log = logging.getLogger(__name__)

class StorageWorkDone(Exception): pass
class StorageIncomplete(Exception): pass
class StorageConnectionFailure(Exception): pass

class Storage(object):
    '''This is a light wrapper around the Google Storage API

        References:
            https://cloud.google.com/storage/docs/json_api/v1/
            https://developers.google.com/resources/api-libraries/documentation/storage/v1/python/latest/storage_v1.buckets.html

        -Examples/cookbook

        # initialize
        gce = Storage(key_file=path)

        # lookup buckets
        buckets = gce.get_buckets()
        bucket  = gce.get_buckets(prefix='myusername')[0]

        # look for a specific bucket
        mybucket = gce.get_bucket(bucket)

        # create a bucket
        bucket  = gce.create_bucket('bucket name')

        # read the contents of a bucket
        objs    = list(gce.read_bucket(bucket))

        # delete some contents of a bucket
        for obj in gce.read_bucket(bucket, buf=10): # buf size optional
            print obj['name']
            gce.delete_object(bucket, obj)

        # download the contents of a bucket
        save_path = '/tmp/bucket_contents'
        for obj in gce.read_bucket(bucket):
            try:
                gce.get_object(bucket, obj, save_path)
            except:
                pass

        # upload objects
        gce.put_object(bucket, '/tmp/data.json', mimetype='text/json')
            - or -
        data_fh = io.StringIO(str_data)
        gce.put_object_fh(bucket, data_fh, filename='my-data.txt', mimetype='text/plain')

        # delete a bucket and all of its contents
        gce.delete_bucket(bucket)

    '''
    DEFAULT_SCOPES=['https://www.googleapis.com/auth/compute',
                    'https://www.googleapis.com/auth/devstorage.read_write']

    def __init__(self, key_file):
        '''Wrapper for Google Storage API
            Parameters:
                key_file: json file path as provided by google

            Returns:
                object

        '''
        self.key_file     = key_file
        with open(self.key_file, 'rb') as f: 
            key_data = json.loads(f.read())
            self.client_email = key_data['client_email']
            self.project_id   = key_data['project_id']

    def auth_http(self):
        '''Create an authorized http object (mainly for use by connection)
            Parameters: None

            Returns:
                http object authorized by credentials
        '''
        from oauth2client.service_account import ServiceAccountCredentials
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.key_file, self.DEFAULT_SCOPES)
        return self.credentials.authorize(httplib2.Http())

    def connection(self):
        '''build the service connection object
            Parameters: None

            Returns:
                storage service object using authorized http

            Raises:
                StorageConnectionFailure

            This is outside of __init__ so that it can be called adhoc in the
            event of a threaded application.  The service object construction
            ifself is lightweight and the composed HTTP object is *not*
            thead-safe.
        '''
        try:
            srv = googleapiclient.discovery.build('storage', 'v1', http=self.auth_http())
            return srv
        except Exception as e:
            raise StorageConnectionFailure("Unable to create storage service object: {}".format(e))

    def gce_do(self, f, retries=3, **options):
        '''GCE function call wrapper with variable retries
            Parameters:
                f: function object to call
                retries: number of retries (defaults to 3)
                **options: options to pass to the function

            Returns:
                Returns function call

            Raises:
                googleapiclient.errors.HttpError
        '''
        tried = 0
        while True:
            try:
                tried += 1
                return f(**options).execute()
            except googleapiclient.errors.HttpError as e:
                log.exception(e)
                if int(e.resp['status']) < 500:
                    raise
                if tried > retries:
                    raise

    def get_buckets(self, prefix=None):
        '''Get all buckets in the project
            Parameters:
                prefix: bucket name prefix (defaults to None)

            Returns:
                a list of bucket dictionaries as returned by google

            The prefix is the mechanism used to limit what is returned, for
            example if you want one particular bucket (you should use the
            get_bucket() wrapper if so).

            The GCE API only allows searching by prefix, so a specific name
            may return more than one if there are other objects with the same
            prefix.
        '''
        c = self.connection()
        buckets = self.gce_do(c.buckets().list,project=self.project_id, prefix=prefix)
        if buckets and 'items' in buckets:
            return buckets['items']
        return []

    def get_bucket(self, bucket_name):
        '''Get a bucket in the project
            Parameters:
                bucket_name: bucket name

            Returns:
                a bucket or None

            This is a wrapper around get_buckets() that looks for an exact
            bucket name match, not just a prefix.
        '''
        buckets = self.get_buckets(bucket_name)
        if not buckets:
            return None

        exact = [i for i in buckets if i['name'] == bucket_name]
        if not exact:
            return None

        return exact[0]


    def create_bucket(self, name):
        '''Create a bucket
            Parameters:
                name: bucket name

            Returns:
                bucket dictionary as returned by google

            Raises:
                googleapiclient.errors.HttpError

            TODO: need naming validation https://cloud.google.com/storage/docs/bucket-naming
        '''
        c = self.connection()
        return self.gce_do(c.buckets().insert,project=self.project_id, body={'name':name})

    def empty_bucket(self, bucket, thread_count=1):
        '''Remove all objects within a bucket
            Parameters:
                bucket: bucket dictionary as returned by google
                thread_count: number of threads to spawn (defaults to 1)

            Returns:
                list of failed deletes, if any, as (object, exception)

            Raises:
                googleapiclient.errors.HttpError
        '''
        c = self.connection()

        if 'name' not in bucket:
            raise TypeError('You must pass the bucket dict as returned from the service')

        log.debug("emptying bucket {}".format(bucket['name']))

        # thread callback
        def thread_cb(service, bucket, q, failq):
            while True:
                obj = q.get()
                # if we are done
                if obj is StorageWorkDone:
                    q.put(obj) # put it back so other threads find it
                    q.task_done()
                    return
                # otherwise do it
                try:
                    service.delete_object(bucket, obj)
                except Exception as e:
                    failq.put((obj, e)) # note failure
                finally:
                    q.task_done()

        q       = Queue.Queue(thread_count)
        failq   = Queue.Queue()
        threads = []

        # start worker threads
        for idx in range(thread_count):
            t = threading.Thread(target=thread_cb, args=(self, bucket, q, failq))
            t.start()
            threads.append(t)

        # iterate over bucket contents, may raise exception
        try:
            for obj in self.read_bucket(bucket=bucket, buf=thread_count):
                q.put(obj)
        except Exception as e:
            failq.put(('Failed to read bucket', e))
        finally:
            q.put(StorageWorkDone) # signal we are done, no need for q.join()

            for t in threads:
                t.join()

        failed = []
        while True:
            try:
                failed.append(failq.get_nowait())
            except Queue.Empty:
                break
        return failed

    def delete_bucket(self, bucket, thread_count=1):
        '''Delete a bucket and all of its contents
            Parameters:
                bucket: bucket dictionary as returned by google
                thread_count: number of threads to spawn (defaults to 1)

            Returns: Nothing

            Raises:
                googleapiclient.errors.HttpError, StorageIncomplete

                StorageIncomplete contains list of (object, exception)

            This calls empty_bucket() prior to actually removing the bucket.
        '''
        c = self.connection()

        if 'name' not in bucket:
            raise TypeError('You must pass the bucket dict as returned from the service')

        failed = self.empty_bucket(bucket, thread_count)

        if not failed:
            log.debug("deleting bucket {}".format(bucket['name']))
            self.gce_do(c.buckets().delete, bucket=bucket['name'])
        else:
            raise StorageIncomplete(failed)

    def delete_object(self, bucket, obj):
        '''Delete an object from a bucket
            Parameters:
                bucket: bucket dictionary as returned by google
                object: object dictionary as returned by google

            Returns: Nothing
        '''
        c = self.connection()

        if any(['name' not in bucket, 'name' not in obj]):
            raise TypeError("You must pass the dict as returned from the service")

        log.debug("deleting {} from bucket {}".format(obj['name'], bucket['name']))
        self.gce_do(c.objects().delete, bucket=bucket['name'], object=obj['name'])

    def get_object_fh(self, bucket, obj, fh, chunksize=1024*1024):
        '''Retrieve the object, writing it to the passed in file handle
            Parameters:
                bucket: bucket dictionary as returned by google
                obj: object dictionary as returned by google
                fh: filehandle (any io.IOBase derived filehandle, even StringIO
                chunksize: size of download chunks (defaults 1024*1024)

            Returns: Nothing

            Raises:
                googleapiclient.errors.HttpError
        '''
        if any(['name' not in bucket, 'name' not in obj]):
            raise TypeError("You must pass the dict as returned from the service")

        c = self.connection()
        req = c.objects().get_media(bucket=bucket['name'], object=obj['name'])
        downloader = googleapiclient.http.MediaIoBaseDownload(fh, req, chunksize)
        try:
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    log.debug("{:>3}% of {} downloaded".format(status.progress() *100, obj['name']))
        except googleapiclient.http.HttpError as e:
            if int(e.resp['status']) < 500:
                raise
            # otherwise should we rewind the filehandle and try again?

    def get_object(self, bucket, obj, dest_path=None, dest_name=None, chunksize=1024*1024):
        '''Retrieve the object into a file following the object name
            Parameters:
                bucket: bucket dictionary as returned by google
                obj: object dictionary as returned by google
                dest_path: destination directory (defaults to cwd)
                dest_name: file name (defaults to object name)
                chunksize: size of download chunks (defaults 1024*1024)

            Returns: Nothing

            Raises:
                googleapiclient.errors.HttpError, IOError, OSError
        '''
        if any(['name' not in bucket, 'name' not in obj]):
            raise TypeError("You must pass the dict as returned from the service")

        if obj['name'][-1] == '/' and int(obj['size']) == 0:
            log.debug("skipping directory entry {}".format(obj['name']))
            return

        if not dest_path:
            dest_path = os.getcwd()
        dest_path = os.path.abspath(dest_path)

        if os.path.exists(dest_path) and not os.path.isdir(dest_path):
            raise ("{} exists and is not a directory".format(dest_path))

        try:
            os.makedirs("{}".format(dest_path))
        except OSError as e:
            if e.errno != 17: # OSError(17, 'File exists')
                raise

        object_path = obj['name'].split(os.sep)
        object_path.pop(-1)
        if object_path:
            try:
                os.makedirs("{}{}{}".format(dest_path, os.sep, os.sep.join(object_path)))
            except OSError as e:
                if e.errno != 17: # OSError(17, 'File exists')
                    raise

        if not dest_name:
            dest_name = obj['name']
        with open("{}{}{}".format(dest_path, os.sep, dest_name), "w") as f:
            self.get_object_fh(bucket, obj, f, chunksize)

    def put_object_fh(self, bucket, fh, filename, chunksize=1024*1024, mimetype='application/octet-stream'):
        '''Put the filehandle contents into an object within a bucket
            Parameters:
                bucket: the dictionary returned from prior service calls
                fh: filehandle (any io.IOBase derived filehandle, even StringIO
                filename: the name of the object (must be unique)
                chunksize: size of upload chunks (defaults 1024*1024)
                mimetype: (defaults to application/octet-stream)

            Returns: Nothing

            Raises:
                googleapiclient.errors.HttpError
        '''
        if 'name' not in bucket:
            raise TypeError("You must pass the dict as returned from the service")

        c = self.connection()

        # using application/octet-stream short of anything more specific as mimetype is
        # required
        media = googleapiclient.http.MediaIoBaseUpload(fh,
                    mimetype=mimetype,
                    chunksize=chunksize,
                    resumable=True)
        req   = c.objects().insert(bucket=bucket['name'], name=filename, media_body=media);

        log.debug("uploading filehandle contents to {}".format(bucket['name']))
        response = None
        while response is None:
            try:
                status, response = req.next_chunk()
                if status:
                    log.debug("{:>3}% of {} uploaded".format(status.progress() *100, filename))
            except googleapiclient.errors.HttpError as e:
                log.exception(e)
                if e.resp.status in [404]: # Start the upload all over again.
                    fh.seek(0,0)
                    media = googleapiclient.http.MediaIOBaseUpload(fh,
                                mimetype='application/octet-stream',
                                chunksize=chunksize,
                                resumable=True)
                    req  = c.object().insert(bucket=bucket['name'], name=filename, media_body=media);
                elif e.resp.status in [500, 502, 503, 504]:
                    time.sleep(2)
                else: # Do not retry. Log the error and fail.
                    fh.close()
                    raise

    def put_object(self, bucket, src_path, chunksize=1024*1024, mimetype='application/octet-stream'):
        '''Put file contents into an object within a bucket
            Parameters:
                bucket: the dictionary returned from prior service calls
                src_path: path to a file
                chunksize: size of upload chunks (defaults 1024*1024)
                mimetype: (defaults to application/octet-stream)

            Returns: Nothing

            This calls put_object_fh() underneath after opening the file. The
            filename passed is the last portion of the file path.  If you need
            more control over the filename itself, use put_object_fh.  This is
            a convenience method.

            This will refuse to upload a directory with a logging.warn().

            Raises:
                googleapiclient.errors.HttpError, IOError
        '''
        if 'name' not in bucket:
            raise TypeError("You must pass the dict as returned from the service")

        if os.path.isdir(src_path):
            log.warn("Refusing to upload a directory: {}".format(src_path))
            return
        with open(src_path, 'r') as f:
            filename = src_path.split(os.sep)[-1]
            log.debug("putting {} into {}".format(filename, bucket['name']))
            self.put_object_fh(bucket, f, chunksize=chunksize, filename=filename, mimetype=mimetype)
            f.close()

    def read_bucket(self, bucket, prefix=None, buf=1):
        '''Returns a generator for iterating through the objects within a bucket
           Parameters:
                bucket: the dictionary returned from prior service calls
                prefix: object name prefix (defaults to None)
                buf: number of objects to fetch at a time (defaults to 1)

            Returns:
                generator for objects

            The prefix is the mechanism used to limit what is returned, for
            example if you want one particular object.

            The GCE API only allows searching by prefix, so a specific name
            may return more than one if there are other objects with the same
            prefix.

        '''
        if 'name' not in bucket:
            raise TypeError("You must pass the dict as returned from the service")

        c = self.connection()
        req = None
        res = None

        if 'name' not in bucket:
            raise TypeError('You must pass the bucket dict as returned from the service')

        while True:
            if not req and not res:
                req = c.objects().list(bucket=bucket['name'], prefix=prefix, maxResults=buf)
                if not req:
                    break
                res = req.execute()
                if 'items' not in res:
                    break;
                for i in res['items']:
                    yield i
            else:
                req = c.objects().list_next(req, res)
                if not req:
                    break
                res = req.execute()
                if 'items' not in res:
                    break;
                for i in res['items']:
                    yield i

