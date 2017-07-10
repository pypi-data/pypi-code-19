from functools import partial

from mongoengine import fields


USLField = partial(fields.ReferenceField, 'USL')
