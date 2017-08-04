from unittest import TestCase

from leryan.types import FastEnum


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

        self.assertIs(type(enum_members), frozenset)
        self.assertEqual(len(enum_members), 3)

    def test_enum_isolation(self):

        class TestEnum1(FastEnum):

            ATTR1 = 1

        class TestEnum2(FastEnum):

            ATTR2 = 2

        self.assertEqual(TestEnum1.ATTR1, 1)
        with self.assertRaises(AttributeError):
            self.assertEqual(TestEnum1.ATTR2, 2)

        with self.assertRaises(AttributeError):
            self.assertEqual(TestEnum2.ATTR1, 1)
        self.assertEqual(TestEnum2.ATTR2, 2)

        enum1_members = TestEnum1.members
        enum2_members = TestEnum2.members

        self.assertNotIn('ATTR2', enum1_members)
        self.assertNotIn('ATTR1', enum2_members)

    def test_enum_values(self):

        class TestEnum(FastEnum):

            ATTR1 = 1
            ATTR2 = 2

        enum_values = TestEnum.values

        self.assertIs(type(enum_values), tuple)
        self.assertEqual(len(enum_values), 2)
        self.assertEqual(TestEnum.ATTR1, 1)
        self.assertEqual(TestEnum.ATTR2, 2)

    def test_enum_contains(self):

        class TestEnum(FastEnum):

            ATTR1 = 1

        self.assertTrue('ATTR1' in TestEnum)
        self.assertFalse('ATTR2' in TestEnum)

    def test_enum_iter(self):

        class TestEnum(FastEnum):

            ATTR1 = 1
            ATTR2 = 2

        for k, v in TestEnum:
            self.assertEqual(getattr(TestEnum, k), v)

    def test_enum_items(self):

        class TestEnum(FastEnum):

            A1 = 1
            A2 = 2
            A3 = 3
            A10 = 10

        test_dict = {'A1': 1, 'A2': 2, 'A3': 3, 'A10': 10}

        self.assertEqual(TestEnum.items(), test_dict)
