#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import

from future.utils import with_metaclass

from myorm.fields import DbField, PkField


class TooManyResultsError(Exception):
    error_code = 1
    pass


class Manager(object):

    def __init__(self, base):
        self.base = base
        self.adaptor = self.base.adaptor

    def _make_objects(self, instance, result):
        objects = []
        for res in result:
            object = instance.__class__()
            mapped = zip(instance.fields, res)
            for field, value in mapped:
                setattr(object, field.fieldname, field.make_value(value))
            objects.append(object)
        return objects

    def filter(self, *args, **kwargs):
        result = self.adaptor.filter(self.base, *args, **kwargs)
        return self._make_objects(self.base, result)

    def all(self):
        return self.filter()

    def get(self, *args, **kwargs):
        result = self.filter(*args, **kwargs)
        if len(result) <= 1:
            try:
                return result[0]
            except IndexError:
                raise IndexError("No %s object found" % self.base.__class__.__name__)
        raise TooManyResultsError('To many results for get(): %s' % len(result))

    def create(self, *args, **kwargs):
        last_id = self.adaptor.create(self.base, **kwargs)
        return self.get(id=last_id)

    def bulk_create(self, objects):
        self.adaptor.bulk_create(objects, self.base)


class MetaType(type):
    def __init__(cls, name, bases, attrs):
        cls.objects = Manager(cls())
        tablename = getattr(cls, 'tablename', None)
        if not tablename or tablename == 'dbobject':
            cls.tablename = cls.__name__.lower()


class DbObject(with_metaclass(MetaType)):
    adaptor = None

    def __init__(self, *args, **kwargs):
        self.id = PkField()
        self.fields = [v for v in self.__class__.__dict__.values() if isinstance(v, DbField)]
        self.fields.append(self.id)
        self.fieldnames = [k for k, v in self.__class__.__dict__.items() if isinstance(v, DbField)]
        self.fieldnames.append('id')

        for name in self.fieldnames:
            field = getattr(self, name)
            setattr(self, name, kwargs.get(name))
            setattr(field, 'fieldname', name)
            setattr(field, 'adaptor', self.adaptor)

    def __repr__(self):
        return "<{0}.{1} object>".format(self.__class__.__module__, self.__class__.__name__)

    @classmethod
    def raw(self, query, *args):
        return self.adaptor._execute_query((query, args))[0]

    def get_settings(self):
        settings = {}
        for fieldname in self.fieldnames:
            value = getattr(self, fieldname)
            print value, fieldname
            if isinstance(value, DbObject):
                value = value.id
            settings[fieldname] = value
        return settings

    @classmethod
    def get_create_table_query(cls, tablename=None):
        return cls.adaptor.get_create_table_query(cls(), tablename)[0]

    @classmethod
    def create_table(cls, tablename=None):
        return cls.adaptor._execute_query((cls.get_create_table_query(), None))

    def delete(self, *args, **kwargs):
        self.adaptor._execute_query(self.adaptor.get_delete_query(self))
        self.id = None

    def save(self, *args, **kwargs):
        if self.id:
            self.adaptor._execute_query(self.adaptor.get_update_query(
                self, *args, filters=[('id', self.id)], **self.get_settings()))
            return self.objects.get(id=self.id)
        last_id = self.adaptor._execute_query(self.adaptor.get_insert_query(self, **self.get_settings()))[1]
        inst = self.objects.get(id=last_id)
        for name in self.fieldnames:
            setattr(self, name, getattr(inst, name))
        return self
