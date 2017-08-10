"""The models architecture defined here is intended to support a declaritive
and extendible means of parsing data into a native python structure.
"""
from __future__ import absolute_import, print_function, unicode_literals

from abc import ABCMeta, abstractmethod
from collections import Mapping, OrderedDict
from itertools import count
from logging import getLogger

import six
from future.utils import python_2_unicode_compatible, raise_with_traceback

from .exceptions import FieldError, ImproperlyConfigured
from .utils import cached_property
from . import validators as _validators


LOGGER = getLogger(__name__)
NOT_FOUND = object()
FIELD_COUNTER = count()

# disable warnings on old-style class definitions (C1001)
# pylint: disable=R0903,W0232,C1001

@python_2_unicode_compatible
class BaseOptions(six.with_metaclass(ABCMeta, Mapping)):
    """A basic options class that can be used to define the set of arguments
    that can be used to parameterize a Field instance or Model subclass by
    extending/overridding the __init__ method.
    """
    @abstractmethod
    def __init__(self, **kwargs):
        """Override this method to define which kwargs are allowed. If extra
        kwargs are provided then ImproperlyConfigured should be raised.
        """
        pass

    def __getitem__(self, name):
        return getattr(self, name, None)

    def __iter__(self):
        return iter({
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith('_')
        })

    def __len__(self):
        return len([key for key in self.__dict__ if not key.startswith('_')])

    def __str__(self):
        return '({})'.format(
            ', '.join(
                ['{}={}'.format(key, value) for key, value in self.items()]
            )
        )

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)


class ModelOptions(BaseOptions):
    """Accepts an old-style Meta class from which the attributes are used
    to set instance attributes. These attributes are the "cleared" model options
    which are mapped directly onto the ModelMeta instance on the Model
    subclasses.
    """
    def __init__(self, meta_cls=None):
        super(ModelOptions, self).__init__()
        kwargs = {}
        if meta_cls:
            meta_cls_options = {
                key: value
                for key, value in meta_cls.__dict__.items()
                if not key.startswith('_')
            }
            kwargs.update(meta_cls_options)
        self.abstract = kwargs.pop('abstract', False)

        if kwargs:
            raise_with_traceback(
                ImproperlyConfigured(
                    'Unsupported model options: {}'.format(
                        ', '.join(kwargs.keys())
                    )
                )
            )


@python_2_unicode_compatible
class ModelMeta(object):
    """Maintains information about the model schema and behavioural options
    defined on the Model subclass. This allows extensabilty throught namespacing
    under the `meta` attribute on the model.
    """
    def __init__(self, model=None, **kwargs):
        self.model = model
        self.fields_map = OrderedDict()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return '{}'.format(', '.join(self.field_names))

    def __repr__(self):
        return '<Meta: {}>'.format(self.model)

    def add_field(self, field):
        """Responsible for adding the Field instance to the set of fields
        registered to the meta.fields.
        """
        field.rel_idx = len(self.fields_map)
        self.fields_map[field.name] = field

    def get_field(self, name):
        return self.fields_map.get(name)

    @property
    def field_names(self):
        return list(self.fields_map.keys())

    @property
    def fields(self):
        return list(self.fields_map.values())


class ModelType(ABCMeta):
    """Modifies Model inheritance such that fields are properly registered
    to the ModelMeta instance in the correct order and options listed under the
    Meta class context are valid and preserved.
    """

    meta_class = ModelMeta
    options_class = ModelOptions

    def __new__(mcs, name, bases, attrs):
        super_new = super(ModelType, mcs).__new__
        parents = [base for base in bases if isinstance(base, ModelType)]

        _meta = attrs.pop('Meta', None)

        if not parents:
            return super_new(mcs, name, bases, attrs)

        new_class = super_new(
            mcs, name, bases, {'__module__': attrs['__module__']}
        )

        new_class.add_meta(_meta)

        for parent in parents:
            new_class.add_parent_fields(parent)

        new_class.add_fields(attrs)

        for attrname, value in attrs.items():
            if hasattr(value, 'add_to_class'):
                value.add_to_class(new_class, attrname)
            else:
                setattr(new_class, attrname, value)
        return new_class

    def add_meta(cls, meta):
        """
        """
        mcs = cls.__class__
        options = mcs.options_class(meta)
        cls.meta = mcs.meta_class(cls, **options)

    def add_fields(cls, attrs):
        """
        """
        fields = [
            (attrname, attrs.pop(attrname))
            for attrname, _ in list(attrs.items())
            if isinstance(_, Field)
        ]
        for attrname, field in sorted(fields, key=lambda item: item[1]._idx):
            field.add_to_class(cls, attrname)

    def add_parent_fields(cls, parent):
        """
        """
        for field in parent.meta.fields:
            field.add_to_class(cls, field.name)


@python_2_unicode_compatible
class Model(six.with_metaclass(ModelType)):
    """Base model template class from which all other models should inherit.
    Usage:
        from ngen import models
        class MyModel(models.Model):
            foo = models.IntegerField(source='dot.path.to.nested.dict.key')
            bar = models.CharField()
    """

    meta = ModelMeta()

    class Meta:  # pylint: disable=C0111
        abstract = True

    def __init__(self, _data=None, **kwargs):
        if _data is not None:
            self.unpack(_data)

        for field_name in self.meta.field_names:
            value = kwargs.pop(field_name, NOT_FOUND)
            if value is NOT_FOUND:
                continue
            setattr(self, field_name, value)

        if kwargs:
            raise_with_traceback(
                ValueError(
                    'Unsupported model kwargs: {}'.format(', '.join(kwargs))
                )
            )

    def unpack(self, data):
        """Parses data using the declared fields to set the instance's
        attributes to the value retrieved by the field.
        By default the data is expected to be a dict structure, however if an
        ordered tuple is expected this method can be overridden.
        """
        for field in self.meta.fields:
            value = field.parse(data)
            setattr(self, field.name, value)
        return self

    def __str__(self):
        return '{}'.format(getattr(self, self.meta.field_names[0], None))

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)


class FieldOptions(BaseOptions):
    """Provides an encapsulated interface that defines the scope of Field
    options that are used to modify the befaviour of each field on a per
    instance basis.
    """
    def __init__(self, field, **kwargs):
        super(FieldOptions, self).__init__()
        self._field = field
        self.source = kwargs.pop('source', None)

        if self.source is not None and not isinstance(self.source, six.string_types):
            raise_with_traceback(
                ImproperlyConfigured(
                    'Field option {}.source is the wrong type. Excpect a '
                    'string and got {}.'.format(self._field, type(self.source))
                )
            )

        self.default = kwargs.pop('default', None)
        self.delimiter = kwargs.pop('delimiter', '.')

        if not isinstance(self.delimiter, six.string_types):
            raise_with_traceback(
                ImproperlyConfigured(
                    'Field option {}.delimiter is the wrong type. Expected '
                    'a string and got {}'.format(
                        self._field,
                        type(self.delimiter)
                    )
                )
            )

        self.validators = kwargs.pop('validators', ())
        self.required = kwargs.pop('required', False)
        self.allow_null = kwargs.pop('allow_null', True)
        self.child = kwargs.pop('child', None)
        if self.child is not None and not isinstance(self.child, Field):
            raise_with_traceback(
                ImproperlyConfigured(
                    'Field option {}.child is the wrong type. Expected an '
                    'instance of a Field subclass but got {}'.format(
                        self._field,
                        type(self.child)
                    )
                )
            )

        self.model = kwargs.pop('model', None)
        if self.model is not None and not isinstance(self.model, ModelType):
            raise_with_traceback(
                ImproperlyConfigured(
                    'Field option {}.model is the wrong type. Expected a '
                    'subclass of Model but got {}'.format(
                        self._field,
                        type(self.model)
                    )
                )
            )

        for key in list(kwargs.keys()):
            if not key.startswith('_'):
                setattr(self, key, kwargs.pop(key))

        if kwargs:
            raise_with_traceback(
                ImproperlyConfigured(
                    'Unsupported field options: {}'.format(
                        ', '.join(kwargs.keys())
                    )
                )
            )


@python_2_unicode_compatible
class Field(six.with_metaclass(ABCMeta)):
    """Base field template from which all field subclasses should inherit
    Usage:
        class CustomField(Field):
            validators = (my_validator_function, )

            def __init__(self, min_length=None, **kwargs):
                super(CustomField, self).__init__(**kwargs)

            def parse(self, value):
                value = super(CustomField, self).parse(value)
                # custom parsing logic
                # ...
                return value
    """

    validators = ()
    name = None
    model = None
    rel_idx = None

    def __init__(self, _idx=None, **kwargs):
        self.options = FieldOptions(self, **kwargs)
        self._idx = _idx or next(FIELD_COUNTER)

    def clean(self, value):
        """Override this method to coerce the data into the type required.
        """
        return value

    def clone(self):
        """Returns a clone of the field using the user defined options. This
        functionality is leveraged when inheriting fields from parent models.
        """
        return type(self)(_idx=self._idx, **self.options)

    def add_to_class(self, model, name):
        """Interfaces with the ModelType factory to register itself with the
        model.
        """
        field = self.clone()
        field.name = name
        field.model = model
        model.meta.add_field(field)

    def parse(self, value):
        """Consumes and parses a (potentially) nested data structure and returns
        the data targeted through the `source` option. If no source option is
        provided then the name is used (which assumes a dict input). If `name`
        is None then the entire value is returned.
        """
        value = self.traverse_path(value)
        if value is None and not self.options.allow_null:
            raise_with_traceback(
                FieldError('{} expected a non-null value'.format(self))
            )
        elif value is NOT_FOUND and self.options.required:
            raise_with_traceback(
                FieldError(
                    '{} is required and could not be found.'.format(self)
                )
            )
        elif value is None and self.options.allow_null:
            return value
        elif value is NOT_FOUND and not self.options.required:
            return self.default
        else:
            self.run_validators(value)
            value = self.clean(value)
        return value

    @cached_property
    def path(self):
        """Cached property used in conjuction with the `traverse_path` method.
        Returns a list of strings can be used to traverse a nested data
        structure.
        """
        return self.get_path()

    def get_path(self):
        if self.options.source is None:
            # if both the source and name are None then it means that the value
            # passed into traverse_path should be returned
            return [self.name] if self.name is not None else []

        return self.options.source.split(self.options.delimiter)

    @property
    def default(self):
        """Returns the default value defined on the field. If a callable was
        defined as the default then the function is called and its output
        returned.
        """
        _default = self.options.default
        if callable(_default):
            return _default()
        return _default

    def traverse_path(self, value):
        """Traversed the value using each part of the `path` property to target
        the desired value.
        Raises a FieldError if an unexpected data type is encountered at any
        given part of the path.
        If the part cannot be found or is null then the method exits with the
        respective signal value i.e. NOT_FOUND or None.
        """
        try:
            for name in self.path:
                if value is NOT_FOUND or value is None:
                    break
                value = value.get(name, NOT_FOUND)
        except AttributeError as exc:
            LOGGER.debug(exc)
            raise_with_traceback(
                FieldError(
                    'Unexpected data type at {}: Got {} expected dict'.format(
                        name, type(value)
                    )
                )
            )
        return value

    def run_validators(self, value):
        """Sequentially runs the user defined field validators and those
        defined on the Field subclass.
        This method is only run if the value was found at the targeted source
        path and was not None.
        """
        for validator in self.options.validators + self.validators:
            value = validator(value)

    def __str__(self):
        return '{}.{}'.format(self.model.__name__, self.name)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)


class ListField(Field):
    """Defines a interface for expected list objects where an optional `child`
    field can be defined to parse the items of the targeted value.
    Usage:
        ListField(child=CharField())
    """
    validators = (_validators.is_list, )

    def parse(self, value):
        value = super(ListField, self).parse(value)
        child = self.options.child
        if child:
            value = [child.parse(item) for item in value]
        return value


class ModelField(Field):
    """Defines a nested data structure interface where models can be nested.
    Usage:

        class Address(models.Model):
            street = models.CharField(source='line_1')
            city = models.CharField()
            country = models.CharField()

        class Person(models.Model):
            name = models.CharField(source='foo.title')
            address = models.ModelField(Address, source='bar.address')

    """
    def __init__(self, model, **kwargs):
        kwargs['child'] = None
        super(ModelField, self).__init__(model=model, **kwargs)

    def parse(self, value):
        value = super(ModelField, self).parse(value)
        return self.options.model(value)


class IntegerField(Field):
    """Simple field that validates the target value is an integer.
    """
    validators = (_validators.is_int, )

    def clean(self, value):
        return int(value)


class CharField(Field):
    """Simple field that validates the target value is any string type.
    """
    validators = (_validators.is_char, )


class BooleanField(Field):
    """Simple field that validates that the target value is a boolean.
    """
    validators = (_validators.is_bool, )
