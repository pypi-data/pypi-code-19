#!/usr/bin/env python
# coding: utf-8


import MySQLdb

from myorm.dbobject import DbObject
from myorm.fields import ForeignKey


class MySQLAdaptor(object):

    def __init__(self, database_settings):
            self.database_settings = database_settings

    def get_connection_and_cursor(self):
        connection = MySQLdb.connect(**self.database_settings)
        cursor = connection.cursor()
        return connection, cursor

    def get_pkfield_create_query(self):
        return '%s INTEGER PRIMARY KEY AUTO_INCREMENT'

    def get_integer_field_create_query(self, default=None):
        query = '%s INTEGER'
        if default is not None:
            query += ' DEFAULT %s' % default
        return query

    def get_char_field_create_query(self, max_length):
        return '%%s CHAR(%s)' % max_length

    def get_text_field_create_query(self):
        return '%s TEXT'

    def get_datetime_field_create_query(self, default):
        if default is None:
            default = '0'
        elif default == 'now':
            default = 'CURRENT_TIMESTAMP'
        return '%%s TIMESTAMP DEFAULT %s' % default

    def get_boolean_field_create_query(self, default):
        return '%%s TINYINT  DEFAULT %s' % default

    def get_foreignkey_field_create_query_base(self):
        return '%s INTEGER'

    def get_foreignkey_field_create_query_extension(self, reference, on_delete):
        if type(DbObject) == type(reference):
            reference = reference.tablename
        return 'FOREIGN KEY(%%s) REFERENCES %s(id)' % (reference)

    def _execute_query(self, query):
        connection, cursor = self.get_connection_and_cursor()
        if not query[1]:
            cursor.execute(query[0])
        else:
            cursor.execute(query[0], query[1])
        connection.commit()
        result = cursor.fetchall()

        cursor.execute("""SELECT last_insert_id()""")
        last_id = cursor.fetchone()[0]

        connection.close()
        return result, last_id

    def _build_filter(self, filter):
        filters = []
        order = ''
        query = ''
        for item in filter:
            if item[0].endswith('__in'):
                filters.append('%s IN (%s)' % (item[0].replace('__in', ''), ', '.join('%s' * len(item[1]))))
            elif item[0].endswith('__lt'):
                filters.append('%s < %s' % (item[0].replace('__lt', ''), '%s'))
            elif item[0].endswith('__lte'):
                filters.append('%s <= %s' % (item[0].replace('__lte', ''), '%s'))
            elif item[0].endswith('__gt'):
                filters.append('%s > %s' % (item[0].replace('__gt', ''), '%s'))
            elif item[0].endswith('__gte'):
                filters.append('%s >= %s' % (item[0].replace('__gte', ''), '%s'))
            elif item[0] == 'order_by':
                direction = 'DESC' if item[1].startswith('-') else 'ASC'
                order += (' ORDER BY %s %s' % (item[1].replace('-', ''), direction))
            else:
                filters.append('%s=%%s' % item[0])
        if filters:
            query = ' WHERE ' + ' AND '.join([item for item in filters])
        return query + order

    def get_create_query(self, cls, tablename):
        if not tablename:
            tablename = cls.tablename
        query = "CREATE TABLE IF NOT EXISTS %s (%%s);" % tablename
        fk_fields = []
        fields = []
        fieldnames = []
        for field in cls.fields:
            if isinstance(field, ForeignKey):
                fk_fields.append(field)
            fields.append(field)
            fieldnames.append(field.fieldname)

        field_queries = [field.partial_create_table_query for field in fields]

        for field in fk_fields:
            fieldnames.append(field.fieldname)
        field_queries.extend([field.partial_create_table_query_extension for field in fk_fields])

        query = query % ', '.join(field_queries)
        query = query % tuple(fieldnames)
        return (query, None)

    def get_select_query(self, cls, *args, **kwargs):
        return ("SELECT %s FROM %s" % (', '.join(cls.fieldnames), cls.tablename), None)

    def get_where_query(self, filters):
        if filters:
            query = "%s" % (self._build_filter(filters))
            return query, tuple([item[1] for item in filters])

    def get_filter_query(self, cls, *args, **kwargs):
        query = self.get_select_query(cls)[0]
        filters = kwargs.items()
        if filters:
            query += self.get_where_query(filters)[0]
            params = []
            for item in filters:
                if item[0] == 'order_by':
                    continue
                if isinstance(item[1], list):
                    for i in item[1]:
                        params.append(i)
                else:
                    params.append(item[1])
            return query, tuple(params)
        return (query, None)

    def get_insert_query(self, cls, *args, **kwargs):
        values = []
        for field in cls.fields:
            value = kwargs.get(field.fieldname)
            if isinstance(value, DbObject):
                value = value.id
            if value is None:
                try:
                    value = field.default
                except AttributeError:
                    pass
            values.append(value)
        query = "INSERT INTO %s (%s) VALUES (%s)" % (cls.tablename,
                                                     ', '.join(cls.fieldnames),
                                                     ', '.join(['%s' for item in cls.fields]))
        return query, tuple(values)

    def get_delete_query(self, cls, filters=None):
        if filters is not None:
            where, values = self.get_where_query(filters)
        else:
            where = "WHERE id=%s"
            values = [cls.id]
        query = "DELETE FROM %s %s" % (cls.tablename, where)
        return query, tuple(values)

    def get_update_query(self, cls, **kwargs):
        filters = kwargs.get('filters')
        if filters:
            kwargs.pop('filters')

        keys = kwargs.keys()
        values = list(kwargs.values())

        settings = ', '.join(['%s=%%s' % item for item in keys])
        query = "UPDATE %s SET %s" % (cls.tablename,
                                      settings)

        filters = self.get_where_query(filters)
        if filters:
            query += filters[0]
            values.extend(filters[1])
        return query, tuple(values)

    def _get_bulk_insert_query(self, objects, base):
        values = [tuple(getattr(item, fieldname) for fieldname in item.fieldnames) for item in objects]
        placeholders = ', '.join(['(%s)' % (', '.join("%s" * len(item))) for item in values])
        query = '''INSERT INTO "%s" (%s) VALUES %s''' % (base.tablename, ', '.join(base.fieldnames), placeholders)
        return query, tuple(v for tupl in values for v in tupl)

    def get_create_table_query(self, base, tablename=None):
        return self.get_create_query(base, tablename)

    def filter(self, base, *args, **kwargs):
        return self._execute_query(self.get_filter_query(base, *args, **kwargs))[0]

    def create(self, base, **kwargs):
        return self._execute_query(self.get_insert_query(base, **kwargs))[1]

    def delete(self, base, filters=None):
        self._execute_query(self.get_delete_query(base, filters))

    def bulk_create(self, objects, base):
        max_params = 999
        max_inserts_per_query = max_params / len(base.fieldnames)
        iterations = (len(base.fieldnames) * len(objects)) / max_params

        lower = 0
        for i in range(0, int(iterations) + 1):
            lower = int(i * max_inserts_per_query)
            upper = int(lower + max_inserts_per_query)
            self._execute_query(self._get_bulk_insert_query(objects[lower:upper], base))
