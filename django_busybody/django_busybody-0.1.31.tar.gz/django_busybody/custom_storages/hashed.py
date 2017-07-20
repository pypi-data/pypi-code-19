# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function

import os
import hashlib
import json
from collections import OrderedDict
from six import text_type, binary_type

import django
from django.conf import settings
from django.utils.functional import cached_property
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles.storage import ManifestFilesMixin
from django.core.files.base import ContentFile

from .overwrite import OverwriteStorageMixin


class HashedStorageMixin(object):
    def _save(self, name, content, *args, **kw):
        s = content.read()
        if isinstance(s, text_type):
            s = s.encode('UTF-8', errors='escape')
        if isinstance(name, binary_type):
            name = name.decode('UTF-8', errors='escape')
        hashv = hashlib.sha1(s).hexdigest()
        hashv = hashv[:2] + os.path.sep + hashv[2:]
        ext = os.path.splitext(name)[1]
        dirname = os.path.dirname(name)
        filename = os.path.join(dirname, hashv + ext)
        return super(HashedStorageMixin, self)._save(filename, content)


class CachedHashValueFilesMixin(object):
    hash_map_filename = '.hash_map.json'

    def __init__(self, *args, **kwargs):
        super(CachedHashValueFilesMixin, self).__init__(*args, **kwargs)
        self.hash_map = self.load_hash_map()

    def _load(self, filename):
        try:
            with self.open(filename) as fp:
                value = fp.read().decode('utf-8')
            return json.loads(value, object_pairs_hook=OrderedDict)
        except (IOError, ValueError):
            return OrderedDict()

    def load_hash_map(self):
        return self._load(self.hash_map_filename)

    def _save(self, name, content, *args, **kw):
        hashv = hashlib.sha1(content.read()).hexdigest()
        if self.hash_map.get(name) == hashv:
            return name
        content.seek(0)
        self.hash_map[name] = hashv
        return super(CachedHashValueFilesMixin, self)._save(name, content, *args, **kw)

    def _dump(self, filename, data):
        if self.exists(filename):
            self.delete(filename)
        contents = json.dumps(data).encode('utf-8')
        self._save(filename, ContentFile(contents))

    def post_process(self, *args, **kwargs):
        if hasattr(super(CachedHashValueFilesMixin, self), 'post_process'):
            all_post_processed = super(
                CachedHashValueFilesMixin, self).post_process(*args, **kwargs)
            for post_processed in all_post_processed:
                yield post_processed
        self._dump(self.hash_map_filename, self.hash_map)


class CachedManifestFilesMixin(CachedHashValueFilesMixin, ManifestFilesMixin):
    hashed_name_map_filename = '.hashed_name_map.json'

    def __init__(self, *args, **kwargs):
        super(CachedManifestFilesMixin, self).__init__(*args, **kwargs)
        self.hashed_name_map = self.load_hashed_name_map()

    def load_hashed_name_map(self):
        return self._load(self.hashed_name_map_filename)

    def _save(self, name, content, *args, **kw):
        hashv = hashlib.sha1(content.read()).hexdigest()
        if self.hash_map.get(name) == hashv:
            return name
        content.seek(0)
        self.hash_map[name] = hashv
        self.hashed_name_map.pop(name, None)
        return super(CachedHashValueFilesMixin, self)._save(name, content, *args, **kw)

    def hashed_name(self, name, content=None, filename=None):
        if name in self.hashed_name_map:
            return self.hashed_name_map[name]

        if django.VERSION[1] >= 11:
            result = super(CachedManifestFilesMixin, self).hashed_name(
                name, content, filename)
        else:
            result = super(CachedManifestFilesMixin, self).hashed_name(
                name, content)

        self.hashed_name_map[name] = result
        return result

    def post_process(self, *args, **kwargs):
        for i in super(CachedManifestFilesMixin, self).post_process(*args, **kwargs):
            yield i
        self._dump(self.hashed_name_map_filename, self.hashed_name_map)


class HashedFileSystemStorage(HashedStorageMixin, OverwriteStorageMixin, FileSystemStorage):
    IGNORE_OVERWRITE = True


class PrivateFileSystemStorage(FileSystemStorage):
    @cached_property
    def location(self):
        return settings.PRIVATE_MEDIA_ROOT


class PrivateHashedFileSystemStorage(HashedStorageMixin, OverwriteStorageMixin, PrivateFileSystemStorage):
    IGNORE_OVERWRITE = True
