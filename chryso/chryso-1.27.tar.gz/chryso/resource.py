import datetime
import logging

import attrdict
from sqlalchemy import select

import chryso.connection
import chryso.errors
import chryso.queryadapter
import chryso.schema

LOGGER = logging.getLogger(__name__)

class Resource():
    TABLE = None
    PROPERTY_CREATION_BLACKLIST = {'created', 'deleted', 'updated'}

    @classmethod
    def _sanitize_kwargs(cls, kwargs):
        for prop in cls.PROPERTY_CREATION_BLACKLIST:
            if prop in kwargs:
                del kwargs[prop]
        for k, v in kwargs.items():
            if isinstance(v, chryso.schema.BaseEnum):
                kwargs[k] = str(v)

    @staticmethod
    def update_filters(filters):
        pass

    @classmethod
    def create(cls, **kwargs):
        engine = chryso.connection.get()
        cls._sanitize_kwargs(kwargs)
        statement = cls.TABLE.insert().values(**kwargs)
        with engine.atomic():
            key = engine.execute(statement).inserted_primary_key[0]
            LOGGER.info("Created new %s with PK %s and content %s", cls.TABLE.name, key, kwargs)
            return key

    @classmethod
    def update(cls, uuid, **kwargs):
        engine = chryso.connection.get()
        cls._sanitize_kwargs(kwargs)
        statement = (
            cls.TABLE.update() #pylint: disable=no-value-for-parameter
                .values(kwargs)
                .where(cls.TABLE.c.uuid == str(uuid))
        )
        engine.execute(statement)
        LOGGER.info("Updated %s with PK %s to have %s", cls.TABLE.name, uuid, kwargs)

    @classmethod
    def delete(cls, uuid):
        engine = chryso.connection.get()
        now = datetime.datetime.utcnow()
        statement = (
            cls.TABLE.update() #pylint: disable=no-value-for-parameter
                .where(cls.TABLE.c.uuid == str(uuid))
                .values(deleted = now)
        )
        engine.execute(statement)
        LOGGER.info("Deleted %s with PK %s to have deleted datetime of %s", cls.TABLE.name, uuid, now.isoformat())

    @classmethod
    def by_uuid(cls, uuid):
        for record in cls.by_filter({'uuid': [uuid]}):
            return record
        raise chryso.errors.RecordNotFound("Could not find a {} record by uuid: {}".format(cls.TABLE.name, uuid))

    @classmethod
    def by_filter(cls, filters):
        engine = chryso.connection.get()
        cls.update_filters(filters)
        query = cls._by_filter_query(filters)
        results = engine.execute(query).fetchall()
        return [attrdict.AttrDict(result) for result in results]

    @classmethod
    def _get_base_query(cls):
        return select([cls.TABLE])

    @classmethod
    def _by_filter_query(cls, filters):
        formatted_filters = chryso.queryadapter.format_filter(filters, {
            'uuid'        : lambda x: [str(u) for u in x],
        })
        filter_map = chryso.queryadapter.map_column_names([cls.TABLE], formatted_filters)
        base_query = cls._get_base_query()
        query = chryso.queryadapter.apply_filter(base_query, filter_map)
        if hasattr(cls.TABLE.c, 'deleted'):
            return query.where(cls.TABLE.c.deleted == None) # pylint: disable=singleton-comparison
        return query
