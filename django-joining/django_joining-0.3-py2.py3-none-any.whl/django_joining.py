from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import cached_property
from django.db.models.fields.related import ForeignObject
from django.db.models.fields.related_descriptors import (
    ForwardManyToOneDescriptor,
    ReverseManyToOneDescriptor, 
)


__all__ = ('JoiningLink', 'JoiningKey')


class ForwardManyToOneJoiningDescriptor(ForwardManyToOneDescriptor):

    def get_object(self, instance):
        try:
            return super().get_object(instance)
        except ObjectDoesNotExist:
            pass


class JoiningLink(ForeignObject):
    """Field for filtering only"""

    requires_unique_target = False

    def __init__(self, to, from_fields, to_fields, **kwargs):
        super().__init__(to, models.DO_NOTHING, from_fields, to_fields, rel=None, 
            related_name='+', parent_link=False, **kwargs)    

    def contribute_to_class(self, cls, name, **kwargs):
        super(ForeignObject, self).contribute_to_class(cls, name, private_only=True, **kwargs)


class JoiningKey(ForeignObject):

    requires_unique_target = False

    related_accessor_class = ReverseManyToOneDescriptor
    forward_related_accessor_class = ForwardManyToOneJoiningDescriptor

    def __init__(self, to, from_fields, to_fields, related_name='+', **kwargs):
        super().__init__(to, models.DO_NOTHING, from_fields, to_fields, rel=None, 
            related_name=related_name, parent_link=False, **kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, private_only=True, **kwargs)

    @staticmethod
    def compiled_instance_value_for_fields(fields):
        return eval('lambda instance: (' + 
            ', '.join(('instance.' + f.attname) for f in fields) + 
            ')')

    @cached_property
    def get_local_related_value(self):
        return self.compiled_instance_value_for_fields(self.local_related_fields)

    @cached_property
    def get_foreign_related_value(self):
        return self.compiled_instance_value_for_fields(self.foreign_related_fields)
