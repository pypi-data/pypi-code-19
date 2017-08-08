import io
import os
import datetime
import posixpath
from urllib.parse import urljoin
from django.core.files import File
from django.utils.encoding import force_text, force_bytes
from oss2 import Auth, Service, BucketIterator, Bucket, ObjectIterator
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.files.storage import Storage
from django.conf import settings
from oss2.api import _normalize_endpoint
from django.utils.deconstruct import deconstructible


class AliyunOperationError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def get_config(name, default=None):
    config = os.environ.get(name, getattr(settings, name, default))
    if config is not None:
        if isinstance(config, str):
            return config.strip()
        else:
            return config
    else:
        msg = "Can't find config for '%s' either in environment variable or in setting.py" % name
        raise ImproperlyConfigured(msg)


def clean_name(name):
    # Normalize Windows style paths
    _clean_name = posixpath.normpath(name).replace('\\', '/')

    # os.path.normpath() can strip trailing slashes so we implement
    # a workaround here.
    if name.endswith('/') and not _clean_name.endswith('/'):
        # Add a trailing slash as it was stripped.
        _clean_name += '/'

    # Given an empty string, os.path.normpath() will return ., which we don't want
    if _clean_name == '.':
        _clean_name = ''

    return _clean_name


class BucketOperationMixin(object):
    def _get_bucket(self, auth):
        return Bucket(auth, self.end_point, self.bucket_name)

    def _list_bucket(self, service):
        return [bucket.name for bucket in BucketIterator(service)]

    def _create_bucket(self, auth):
        bucket = self._get_bucket(auth)
        bucket.create_bucket(settings.BUCKET_ACL_TYPE)
        return bucket

    def _check_bucket_acl(self, bucket):
        if bucket.get_bucket_acl().acl != settings.OSS_BUCKET_ACL_TYPE:
            bucket.put_bucket_acl(settings.OSS_BUCKET_ACL_TYPE)
        return bucket


@deconstructible
class BaseStorage(BucketOperationMixin, Storage):
    location = ""

    def __init__(self):
        self.access_key_id = get_config('OSS2_ACCESS_KEY_ID')
        self.access_key_secret = get_config('OSS2_ACCESS_KEY_SECRET')
        self.end_point = _normalize_endpoint(get_config('OSS2_END_POINT').strip())
        self.bucket_name = get_config('OSS2_BUCKET_NAME')

        self.auth = Auth(self.access_key_id, self.access_key_secret)
        self.service = Service(self.auth, self.end_point)

        if self.bucket_name not in self._list_bucket(self.service):
            self.bucket = self._create_bucket(self.auth)
        else:
            self.bucket = self._check_bucket_acl(self._get_bucket(self.auth))

    def _normalize_name(self, name):
        base_path = force_text(self.location).rstrip('/')
        final_path = urljoin(base_path.rstrip('/') + "/", name)
        base_path_len = len(base_path)
        if not final_path.startswith(base_path) or final_path[base_path_len:base_path_len + 1] not in ('', '/'):
            msg = "Attempted access to '%s' denied." % name
            raise SuspiciousOperation(msg)
        return final_path.lstrip('/')

    def _get_target_name(self, name):
        name = self._normalize_name(clean_name(name))
        return name

    def _open(self, name, mode='rb'):
        return Oss2File(name, self, mode)

    def _save(self, name, content):
        target_name = self._get_target_name(name)
        content.open()
        content_str = b''.join(chunk for chunk in content.chunks())
        self.bucket.put_object(target_name, content_str)
        content.close()
        return clean_name(name)

    def get_file_header(self, name):
        name = self._get_target_name(name)
        return self.bucket.head_object(name)

    def exists(self, name):
        return self.bucket.object_exists(name)

    def size(self, name):
        file_info = self.get_file_header(name)
        return file_info.content_length

    def modified_time(self, name):
        file_info = self.get_file_header(name)
        return datetime.datetime.fromtimestamp(file_info.last_modified)

    def listdir(self, name):
        name = self._normalize_name(clean_name(name))
        if name and name.endswith('/'):
            name = name[:-1]

        files = []
        dirs = set()

        for obj in ObjectIterator(self.bucket, prefix=name, delimiter='/'):
            if obj.is_prefix():
                dirs.add(obj.key)
            else:
                files.append(obj.key)

        return list(dirs), files

    def url(self, name):
        name = self._normalize_name(clean_name(name))
        name = name.encode('utf8')
        return self.bucket._make_url(self.bucket_name, name)

    def read(self, name):
        pass

    def delete(self, name):
        name = self._get_target_name(name)
        result = self.bucket.delete_object(name)
        if result.status >= 400:
            raise AliyunOperationError(result.resp)


class Oss2MediaStorage(BaseStorage):
    location = settings.MEDIA_URL


class Oss2StaticStorage(BaseStorage):
    location = settings.STATIC_URL


@deconstructible
class Oss2File(File):
    def __init__(self, name, storage, mode):
        self._storage = storage
        self._name = name[len(self._storage.location) + 1:]
        self._mode = mode
        self.file = io.BytesIO()
        self._is_dirty = False
        self._is_read = False
        super().__init__(self.file, self.name)

    def read(self, num_bytes=None):
        if not self._is_read:
            content = self._storage.bucket.get_object(self._name)
            self.file = io.BytesIO(content)
            self._is_read = True

        if num_bytes is None:
            data = self.file.read()
        else:
            data = self.file.read(num_bytes)

        if 'b' in self._mode:
            return data
        else:
            return force_text(data)

    def write(self, content):
        if 'w' not in self._mode:
            raise AliyunOperationError("Operation write is not allowed.")

        self.file.write(force_bytes(content))
        self._is_dirty = True
        self._is_read = True

    def close(self):
        if self._is_dirty:
            self.file.seek(0)
            self._storage._save(self._name, self.file)
        self.file.close()
