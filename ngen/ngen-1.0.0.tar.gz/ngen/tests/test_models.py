from __future__ import unicode_literals, print_function, absolute_import

import unittest

try:
    import mock
except ImportError:
    from unittest import mock

from ngen.exceptions import ValidationError
from ngen.models import (
    BaseOptions,
    BooleanField,
    CharField,
    Field,
    FieldError,
    FieldOptions,
    ImproperlyConfigured,
    IntegerField,
    ListField,
    Model,
    ModelField,
    ModelMeta,
    ModelOptions,
    ModelType,
    NOT_FOUND
)


class TestBaseOptions(unittest.TestCase):

    class TempOptions(BaseOptions):

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    options = TempOptions(_missing=True, here=True)

    class IncompleteOptions(BaseOptions):
        pass

    def test_IncompleteOptions_raises_when_instantiated(self):
        self.assertRaises(TypeError, self.IncompleteOptions)

    def test_len_equals_iter_len(self):
        self.assertEqual(len(self.options), len(dict(self.options)))
        self.assertEqual(len(self.options), 1)

    def test_mapping(self):
        def func(**kwargs):
            return kwargs
        self.assertEqual(func(**self.options), {'here': True})

    def test_str(self):
        self.assertEqual(str(self.options), '(here=True)')

    def test_repr(self):
        self.assertEqual(repr(self.options), '<TempOptions: (here=True)>')

    def test_iter(self):
        self.assertEqual(dict(self.options), {'here': True})


class TestModelOptions(unittest.TestCase):

    def test_is_subclass_of_BaseOptions(self):
        self.assertTrue(issubclass(ModelOptions, BaseOptions))

    def test_init_with_no_meta_cls(self):
        options = ModelOptions()
        self.assertFalse(options.abstract)

    def test_init_with_meta_cls(self):
        class Meta:
            abstract = True

        options = ModelOptions(Meta)
        self.assertTrue(options.abstract)

    def test_init_with_meta_cls_unknown_options(self):
        class Meta:
            unknown = 'value'

        self.assertRaises(ImproperlyConfigured, ModelOptions, Meta)


class TestModelMeta(unittest.TestCase):

    def test_init_defaults(self):
        meta = ModelMeta()
        self.assertIsNone(meta.model)
        self.assertEqual(meta.fields, [])
        self.assertEqual(meta.field_names, [])

    def test_init_kwargs_mapping(self):
        meta = ModelMeta(test=True)
        self.assertTrue(meta.test)

    def test_str(self):
        meta = ModelMeta()

        field1 = mock.MagicMock()
        field1.name = 'foo'
        meta.add_field(field1)

        field2 = mock.MagicMock()
        field2.name = 'bar'
        meta.add_field(field2)

        self.assertEqual(str(meta), 'foo, bar')

    def test_repr(self):
        meta = ModelMeta()
        meta.model = 'test'
        self.assertEqual(repr(meta), '<Meta: test>')

    def test_add_field(self):
        meta = ModelMeta()
        field = mock.MagicMock()
        field.name = 'test'
        meta.add_field(field)
        self.assertEqual(field.rel_idx, 0)
        self.assertTrue(field in meta.fields)
        self.assertTrue('test' in meta.field_names)

    def test_add_field_with_field_replacement(self):
        meta = ModelMeta()

        field1 = mock.MagicMock()
        field1.name = 'foo'
        meta.add_field(field1)

        field2 = mock.MagicMock()
        field2.name = 'bar'
        meta.add_field(field2)

        self.assertTrue(meta.get_field('foo'), field1)
        self.assertTrue(meta.fields[0], field1)
        self.assertTrue(meta.fields[1], field2)

        field3 = mock.MagicMock()
        field3.name = 'foo'
        meta.add_field(field3)

        self.assertTrue(meta.get_field('foo'), field3)
        self.assertTrue(meta.fields[0], field3)
        self.assertTrue(meta.fields[1], field2)


class TestModelType(unittest.TestCase):

    def test_meta_class_attr(self):
        self.assertEqual(ModelType.meta_class, ModelMeta)

    def test_options_class(self):
        self.assertEqual(ModelType.options_class, ModelOptions)

    def test_Meta_is_not_an_attribute(self):
        class Meta:
            abstract = False

        model = ModelType.__new__(
            ModelType,
            str('SomeModel'),
            (Model, ),
            {'Meta': Meta, '__module__': 'foo'}
        )
        self.assertFalse(hasattr(model, 'Meta'))

    def test_add_meta(self):
        with mock.patch.object(ModelType, 'meta_class') as meta_class:
            with mock.patch.object(ModelType, 'options_class') as options_class:
                options_class.return_value = {}
                meta = mock.MagicMock()
                meta_class.return_value = meta
                _meta = mock.MagicMock()
                model = ModelType.__new__(
                    ModelType,
                    str('SomeModel'),
                    (Model, ),
                    {'Meta': _meta, '__module__': 'foo'}
                )
                options_class.assert_called_once_with(_meta)
                meta_class.assert_called_once_with(model)
                self.assertEqual(model.meta, meta)

    def test_add_parent_fields(self):
        with mock.patch.object(Model, 'meta') as meta:
            field = mock.MagicMock()
            field.add_to_class = mock.MagicMock()
            meta.fields = [field]

            model = ModelType.__new__(
                ModelType,
                str('SomeModel'),
                (Model, ),
                {'__module__': 'foo'}
            )

            self.assertTrue(field.add_to_class.called)
            field.add_to_class.assert_called_once_with(
                model, field.name
            )

    def test_add_fields(self):
        field = CharField()
        with mock.patch.object(field, 'add_to_class') as add_to_class:
            model = ModelType.__new__(
                ModelType,
                str('SomeModel'),
                (Model, ),
                {'__module__': 'foo', 'foo': field}
            )
            self.assertFalse(hasattr(model, 'foo'))
            self.assertTrue(add_to_class.called)
            add_to_class.assert_called_once_with(model, 'foo')

    def test_attribute_instances_with_add_to_class_method(self):
        thing = mock.MagicMock()
        thing.add_to_class = mock.MagicMock()
        model = ModelType.__new__(
            ModelType,
            str('SomeModel'),
            (Model, ),
            {'__module__': 'foo', 'foo': thing}
        )
        self.assertTrue(thing.add_to_class.called)
        thing.add_to_class.assert_called_once_with(model, 'foo')

    def test_regular_attribute(self):
        model = ModelType.__new__(
            ModelType,
            str('SomeModel'),
            (Model, ),
            {'__module__': 'foo', 'foo': 'bar'}
        )
        self.assertTrue(hasattr(model, 'foo'))
        self.assertEqual(model.foo, 'bar')


class TestModels(unittest.TestCase):

    class Friend(Model):
        name = CharField()
        age = IntegerField()
        surname = CharField(source='last_name')

    class Entity(Model):
        id = IntegerField(required=True, allow_null=False)
        first_name = CharField(source='name')
        tags = ListField(source='foo.tags')

    def setUp(self):
        self.data = {
            'id': 1,
            'name': 'larry',
            'url': 'google.com',
            'foo': {
                'bar': 2,
                'tags': ['cool', 'easy'],
            },
            'friends': [
                {'name': 'bob', 'age': 24},
                {'name': 'alice', 'age': None, 'last_name': 'secret'}
            ]
        }

    def test_meta_fields_order(self):
        self.assertEqual(self.Friend.meta.field_names, ['name', 'age', 'surname'])
        self.assertEqual(self.Entity.meta.field_names, ['id', 'first_name', 'tags'])

    def test_meta_fields_order_inheritance(self):
        class Person(self.Entity):
            friends = ListField(child=ModelField(self.Friend))

        self.assertEqual(
            Person.meta.field_names,
            ['id', 'first_name', 'tags', 'friends']
        )

    def test_init_with_data(self):
        with mock.patch.object(self.Entity, 'unpack') as unpack:
            self.Entity(self.data)
            self.assertTrue(unpack.called)
            unpack.assert_called_once_with(self.data)

    def test_init_with_valid_kwargs(self):
        entity = self.Entity(first_name='bob')
        self.assertEqual(entity.first_name, 'bob')

    def test_init_with_invalid_kwargs(self):
        self.assertRaises(ValueError, self.Entity, foo='bar')

    def test_unpack(self):
        entity = self.Entity()
        entity.unpack(self.data)
        self.assertEqual(entity.first_name, 'larry')
        self.assertEqual(entity.id, 1)
        self.assertEqual(entity.tags, ['cool', 'easy'])

    def test_str(self):
        entity = self.Entity(id=10)
        self.assertEqual(str(entity), '10')

        entity = self.Entity()
        self.assertEqual(str(entity), 'None')

    def test_repr(self):
        entity = self.Entity(id=10)
        self.assertEqual(repr(entity), '<Entity: 10>')


class TestFieldOptions(unittest.TestCase):

    def test_init_with_valid_kwargs(self):
        options = FieldOptions(None, random=True)
        self.assertTrue(options.random)

    def test_init_with_invalid_kwargs(self):
        self.assertRaises(ImproperlyConfigured, FieldOptions, None, _foo='bar')

    def test_raises_on_invalid_source(self):
        self.assertRaises(ImproperlyConfigured, FieldOptions, None, source=1)

    def test_raises_on_invalid_delimiter(self):
        self.assertRaises(ImproperlyConfigured, FieldOptions, None, delimiter=1)

    def test_raises_on_invalid_child(self):
        self.assertRaises(ImproperlyConfigured, FieldOptions, None, child=1)

    def test_raises_on_invalid_model(self):
        self.assertRaises(ImproperlyConfigured, FieldOptions, None, model=1)


class TestFields(unittest.TestCase):

    def setUp(self):
        # bust the path cache
        self.field.__dict__.pop('path', None)

    class CustomField(Field):
        pass

    model = mock.MagicMock()
    model.__name__ = 'model'
    field = CustomField()
    field.name = 'foo'
    field.model = model

    def test_options_namespacing_of_kwargs(self):
        self.assertIsNotNone(self.field._idx)

    def test_clean(self):
        value = mock.MagicMock()
        self.assertEqual(self.field.clean(value), value)

    def test_clone(self):
        clone = self.field.clone()
        self.assertIsInstance(clone, self.CustomField)
        self.assertFalse(clone is self.field)

    def test_add_to_class_hits_clone(self):
        with mock.patch.object(self.field, 'clone') as clone:
            self.field.add_to_class(mock.MagicMock(), 'foo')
            self.assertTrue(clone.called)

    def test_add_to_class_hits_model_meta_add_field(self):
        with mock.patch.object(self.field, 'clone') as clone:
            model = mock.MagicMock()
            self.field.add_to_class(model, 'foo')
            self.assertTrue(model.meta.add_field.called)
            model.meta.add_field.assert_called_once_with(clone.return_value)

    def test_parse_hits_traverse_path(self):
        with mock.patch.object(self.field, 'traverse_path') as traverse_path:
            value = mock.MagicMock()
            output = self.field.parse(value)
            self.assertTrue(traverse_path.called)
            self.assertEqual(output, traverse_path.return_value)

    def test_parse_raises_FieldError_on_allow_null_False(self):
        self.field.options.allow_null = False
        with mock.patch.object(self.field, 'traverse_path') as traverse_path:
            traverse_path.return_value = None
            self.assertRaises(FieldError, self.field.parse, None)

        self.field.options.allow_null = True

    def test_parse_raises_when_not_found_and_required(self):
        self.field.options.required = True
        with mock.patch.object(self.field, 'traverse_path') as traverse_path:
            traverse_path.return_value = NOT_FOUND
            self.assertRaises(FieldError, self.field.parse, None)
        self.field.options.required = False

    def test_parse_returns_default_when_not_found_and_not_required(self):
        with mock.patch.object(self.field, 'traverse_path') as traverse_path:
            traverse_path.return_value = NOT_FOUND
            self.assertEqual(
                self.field.parse(mock.MagicMock()),
                self.field.default
            )

    def test_parse_returns_None_when_null_value_is_found_and_is_allowed(self):
        with mock.patch.object(self.field, 'traverse_path') as traverse_path:
            traverse_path.return_value = None
            self.assertEqual(
                self.field.parse(mock.MagicMock()),
                None
            )

    def test_parse_hits_run_validators_when_non_None_value_is_found(self):
        with mock.patch.object(self.field, 'traverse_path') as traverse_path:
            with mock.patch.object(self.field, 'run_validators') as run_validators:
                value = mock.MagicMock()
                self.field.parse(value)
                self.assertTrue(run_validators.called)
                run_validators.assert_called_once_with(traverse_path.return_value)

    def test_parse_hits_clean_when_non_None_value_is_found(self):
         with mock.patch.object(self.field, 'traverse_path') as traverse_path:
            with mock.patch.object(self.field, 'clean') as clean:
                value = mock.MagicMock()
                self.field.parse(value)
                self.assertTrue(clean.called)
                clean.assert_called_once_with(traverse_path.return_value)

    def test_path_is_name_when_source_is_None(self):
        self.assertEqual(self.field.get_path(), [self.field.name])

    def test_path_is_empty_when_source_and_name_are_None(self):
        self.field.name = None
        self.assertEqual(self.field.get_path(), [])
        self.field.name = 'foo'

    def test_path_is_cached(self):
        with mock.patch.object(self.field, 'get_path') as get_path:
            self.assertEqual(self.field.path, get_path.return_value)
            self.assertTrue(get_path.called)
            self.assertEqual(get_path.call_count, 1)
            self.field.path
            self.assertEqual(get_path.call_count, 1)

    def test_path_on_source(self):
        self.field.options.source = 'some.dot.path'
        self.assertEqual(self.field.get_path(), ['some', 'dot', 'path'])

    def test_default_on_callable(self):
        self.field.options.default = dict
        default = self.field.default
        self.assertIsInstance(default, dict)
        self.assertFalse (self.field.default is default)
        self.field.options.default = None

    def test_default_on_constant(self):
        self.field.options.default = 'hello'
        self.assertEqual(self.field.default, 'hello')
        self.field.options.default = None

    def test_traverse_path_on_inconsistent_data(self):
        self.field.options.source = 'foo.bar'
        self.assertRaises(FieldError, self.field.traverse_path, {'foo': 1})
        self.field.options.source = None

    def test_traverse_path_on_valid_path(self):
        self.field.options.source = 'foo.bar'
        self.assertEqual(
            self.field.traverse_path({'foo': {'bar': 1}}),
            1
        )
        self.field.options.source = None

    def test_traverse_path_on_incomplete_data(self):
        self.field.options.source = 'foo.bar'
        self.assertEqual(
            self.field.traverse_path({'foo': {'baz': 1}}),
            NOT_FOUND
        )
        self.field.options.source = None

    def test_traverse_path_on_null_value(self):
        self.field.options.source = 'foo.bar'
        self.assertEqual(
            self.field.traverse_path({'foo': None}),
            None
        )
        self.field.options.source = None

    def test_run_validators_both_options_and_core_hit(self):

        def side_effect(value):
            return value

        fake_validator1 = mock.MagicMock(side_effect=side_effect)
        fake_validator2 = mock.MagicMock(side_effect=side_effect)
        self.field.validators = (fake_validator1,)
        self.field.options.validators = (fake_validator2, )

        self.field.run_validators(None)
        self.assertTrue(fake_validator1.called)
        fake_validator1.assert_called_once_with(None)
        self.assertTrue(fake_validator2.called)
        fake_validator2.assert_called_once_with(None)

    def test_str(self):
        self.assertEqual(str(self.field), 'model.foo')

    def test_repr(self):
        self.assertEqual(repr(self.field), '<CustomField: model.foo>')

    def test_ListField_parse_calls_child_parse(self):
        field = ListField(child=CharField())
        with mock.patch.object(field.options.child, 'parse') as parse:
            field.parse(['foo', 'bar'])
            self.assertTrue(parse.called)
            self.assertEqual(parse.call_count, 2)
            parse.assert_called_with('bar')
            parse.assert_any_call('foo')

    def test_ModelField_parse_returns_instance_of_model(self):
        class TestModel(Model):
            foo = CharField()

        field = ModelField(TestModel)
        value = field.parse({'foo': 'bar'})
        self.assertIsInstance(value, TestModel)
        self.assertEqual(value.foo, 'bar')

    def test_IntegerField_validators(self):
        field = IntegerField()
        self.assertRaises(ValidationError, field.run_validators, None)
        self.assertEqual(field.run_validators(1), None)

    def test_IntegerField_clean_coerces_int(self):
        field = IntegerField()
        self.assertEqual(field.clean('1'), 1)

    def test_CharField_validators(self):
        field = CharField()
        self.assertRaises(ValidationError, field.run_validators, None)
        self.assertEqual(field.run_validators('foo'), None)

    def test_BooleanField_validators(self):
        field = BooleanField()
        self.assertRaises(ValidationError, field.run_validators, None)
        self.assertEqual(field.run_validators(False), None)


# the following is here to help with debugging
if __name__ == '__main__':
    unittest.main()
