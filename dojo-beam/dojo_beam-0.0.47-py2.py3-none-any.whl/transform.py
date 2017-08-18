from __future__ import absolute_import, print_function, unicode_literals

import random
import apache_beam as beam

from dojo.transform import Transform
from dojo.transforms import Conform as VanillaConform, \
    Validate as VanillaValidate, \
    ConvertFrom as VanillaConvertFrom, \
    ConvertTo as VanillaConvertTo, \
    KeyBy as VanillaKeyBy, \
    DeKey as VanillaDeKey


@beam.ptransform_fn
def DistinctBy(pcoll, key, sort_keys=None):

    def _reduce(rows):
        if sort_keys:
            rows = sorted(rows, key=lambda r: [r[k] for k in sort_keys])
        else:
            rows = sorted(rows)
        return rows[0]

    return (pcoll | beam.ParDo(KeyBy(key))
                  | beam.CombinePerKey(_reduce)
                  | beam.ParDo(DeKey()))


@beam.ptransform_fn
def LeftOuterJoin(left_pcoll, right_pcoll, left_key, right_key=None, sort_keys=None, mapping=None):

    def _merge(kv):
        key, joined = kv
        left_rows = joined['left']
        right_rows = joined['right']
        if len(right_rows) == 0:
            return left_rows
        if len(left_rows) == 0:
            return []
        if len(right_rows) > 1:
            raise ValueError('expected many-to-1 join but there are %s RHS rows' % (len(right_rows), ))
        right_row = right_rows[0]
        for row in left_rows:
            if mapping is None:
                row.update(right_row)
            else:
                for right_key, left_key in mapping.items():
                    if right_key in right_row:
                        row[left_key] = right_row[right_key]
        return left_rows

    if right_key is None:
        right_key = left_key
    join = {
        'left': left_pcoll | 'join %s left' % (random.randint(0, 100), ) >> beam.ParDo(KeyBy(left_key)),
        'right': right_pcoll | 'join %s right' % (random.randint(0, 100), ) >> beam.ParDo(KeyBy(right_key))
    }
    return (join | beam.CoGroupByKey()
                 | beam.FlatMap(_merge))


class BeamTransform(Transform, beam.DoFn):

    def process(self, row):
        raise NotImplementedError()


class SetValue(BeamTransform):

    def __init__(self, key, value, *args, **kwargs):
        self.key = key
        self.value = value
        super(SetValue, self).__init__(*args, **kwargs)

    def process(self, row):
        row[self.key] = self.value
        return [row, ]


class Conform(VanillaConform, beam.DoFn):

    def process(self, row):
        # apache_beam.typehints.decorators.TypeCheckError: Returning a dict from a ParDo or FlatMap is discouraged
        return [super(Conform, self).process(row), ]


class Validate(VanillaValidate, beam.DoFn):

    def process(self, row):
        return [super(Validate, self).process(row), ]


class ConvertFrom(VanillaConvertFrom, beam.DoFn):

    def process(self, row):
        return [super(ConvertFrom, self).process(row), ]


class ConvertTo(VanillaConvertTo, beam.DoFn):

    def process(self, row):
        return [super(ConvertTo, self).process(row), ]


class KeyBy(VanillaKeyBy, beam.DoFn):

    def process(self, row):
        return [super(KeyBy, self).process(row), ]


class DeKey(VanillaDeKey, beam.DoFn):

    def process(self, row):
        return [super(DeKey, self).process(row), ]
