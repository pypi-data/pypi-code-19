from base10.base import Metric
from base10.exceptions import Base10Error


class MetricHelper(Metric):
    __initialised__ = False

    def __new__(cls, *args, **kwargs):
        if not cls.__initialised__:
            if 'name' in kwargs:
                cls._name = kwargs.pop('name')
            else:
                if not hasattr(cls, '_name'):
                    raise Base10Error('_name is required')

            if 'fields' in kwargs:
                cls._fields = kwargs.pop('fields')
            else:
                if not hasattr(cls, '_fields'):
                    raise Base10Error('_fields is required')

            if 'metadata' in kwargs:
                cls._metadata = kwargs.pop('metadata')
            else:
                if not hasattr(cls, '_metadata'):
                    raise Base10Error('_metadata is required')

            if 'time' in cls._fields:
                cls._fields.remove('time')

            cls.__initialised__ = True

        return super(Metric, cls).__new__(cls)  # , *args, **kwargs)

    def __init__(self, **kwargs):
        kwargs.pop('name', None)
        kwargs.pop('fields', None)
        kwargs.pop('metadata', None)

        self._verify_and_store(kwargs)


class MetricHandler(object):

    def __init__(self, *args, **kwargs):
        if not hasattr(self, '_reader') and not hasattr(self, '_writer'):
            raise Base10Error('Either _reader or _writer is required')

        if not hasattr(self, '_dialect'):
            raise Base10Error('_dialect is required')

    def read(self):
        try:
            while True:
                yield self._dialect.from_string(next(self._reader.read()))
        except AttributeError as e:
            raise Base10Error('Attempt to read from a write-only MetricHandler',
                              e)

    def write(self, metric):
        try:
            return self._writer.write(self._dialect.to_string(metric))
        except AttributeError as e:
            raise Base10Error('Attempt to write to a read-only MetricHandler',
                              e)
