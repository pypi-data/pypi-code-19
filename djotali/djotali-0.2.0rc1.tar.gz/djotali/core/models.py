# coding: utf-8
from django.db.backends.oracle.functions import IntervalToSeconds
from model_utils.models import SoftDeletableModel, TimeStampedModel


class IntervalToSecondsNoSqlite(IntervalToSeconds):
    def __init__(self, expression, **extra):
        super(IntervalToSecondsNoSqlite, self).__init__(expression, **extra)

    def as_sql(self, compiler, connection, function=None, template=None, arg_joiner=None, **extra_context):
        if connection.vendor == 'sqlite':
            template = '%(expressions)s'
        return super().as_sql(compiler, connection, function, template, arg_joiner, **extra_context)


class TrackedModel(TimeStampedModel, SoftDeletableModel):
    class Meta:
        abstract = True
