from enum import Enum

from sqlalchemy import Column, DateTime, MetaData, Table, func, text
from sqlalchemy.dialects.postgresql import UUID

import chryso.constants

metadata = MetaData(naming_convention=chryso.constants.CONVENTION)

class BaseEnum(Enum):
    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return [str(v) for v in cls]

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return str(self)

def table(name, *args, **kwargs):
    return Table(
        name,
        metadata,
        Column('uuid', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        Column('created', DateTime, server_default=func.now(), nullable=False),
        Column('updated', DateTime, server_default=func.now(), onupdate=func.now(), nullable=False),
        Column('deleted', DateTime, nullable=True),
        *args,
        **kwargs
    )
