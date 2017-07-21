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