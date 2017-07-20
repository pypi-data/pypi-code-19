# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

from django.core.files.storage import FileSystemStorage


class OverwriteStorageMixin(object):
    IGNORE_OVERWRITE = False

    def _save(self, name, content):
        if self.IGNORE_OVERWRITE and self.exists(name):
            return name
        self.delete(name)
        return super(OverwriteStorageMixin, self)._save(name, content)

    def get_available_name(self, name, *args, **kw):
        return name


class IgnoreDeleteStorageMixin(object):
    def delete(self, *args, **kwargs):
        pass


class OverwriteSystemStorage(OverwriteStorageMixin, FileSystemStorage):
    IGNORE_OVERWRITE = False
