#!/usr/bin/env python
# coding: utf-8


class DbField(object):

    def make_value(self, value):
        return value


class PkField(DbField):

    def __init__(self):
        self.fieldname = 'id'

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_pkfield_create_query()


class IntegerField(DbField):

    def __init__(self, default=None):
        self.default = default

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_integer_field_create_query(self.default)


class CharField(DbField):

    def __init__(self, max_length):
        self.max_length = max_length

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_char_field_create_query(self.max_length)


class TextField(DbField):

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_text_field_create_query()


class BooleanField(DbField):

    def __init__(self, default):
        self.default = default

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_boolean_field_create_query(self.default)


class DateTimeField(DbField):

    def __init__(self, default=None):
        self.default = default

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_datetime_field_create_query(self.default)


class ForeignKey(DbField):

    def __init__(self, reference, on_delete=None):
        self.reference = reference
        self.on_delete = on_delete

    def make_value(self, value):
        reference_obj = self.reference.objects.filter(id=value)
        if not reference_obj:
            return None
        return reference_obj[0]

    @property
    def partial_create_table_query(self):
        return self.adaptor.get_foreignkey_field_create_query_base()

    @property
    def partial_create_table_query_extension(self):
        return self.adaptor.get_foreignkey_field_create_query_extension(self.reference, self.on_delete)
