from unittest import TestCase

from leryan.types import ObjectDict
from leryan.types import FastEnum


class ObjectDictTest(TestCase):

    def test_create(self):
        a = ObjectDict()

        a.attribute = 'value'

        self.assertEqual(a.attribute, 'value')
        self.assertEqual(a['attribute'], 'value')

    def test_create_from_dict(self):
        a = ObjectDict({'attribute': 'value'})

        self.assertEqual(a.attribute, 'value')
        self.assertEqual(a['attribute'], 'value')


class FastEnumTest(TestCase):

    def test_enum(self):
        class TestEnum(FastEnum):

            ATTRIBUTE = 'value'
            OTHER_ATTRIBUTE = 0

        self.assertEqual(TestEnum.ATTRIBUTE, 'value')
        self.assertEqual(TestEnum.OTHER_ATTRIBUTE, 0)

    def test_enum_cannot_reassign(self):
        class TestEnum(FastEnum):

            EXISTING_ATTRIBUTE = 0

        with self.assertRaises(AttributeError):
            TestEnum.EXISTING_ATTRIBUTE = 1

        with self.assertRaises(AttributeError):
            TestEnum.NEW_ATTRIBUTE = 2

    def test_enum_members(self):
        class TestEnum(FastEnum):

            ATTR1 = 0
            attr2 = 0
            Attr3 = 0
            _hidden_attr = 0
            __hidden_attr = 0


        enum_members = TestEnum.members

        self.assertIn('ATTR1', enum_members)
        self.assertIn('attr2', enum_members)
        self.assertIn('Attr3', enum_members)
        self.assertNotIn('_hidden_attr', enum_members)
        self.assertNotIn('__hidden_attr', enum_members)
