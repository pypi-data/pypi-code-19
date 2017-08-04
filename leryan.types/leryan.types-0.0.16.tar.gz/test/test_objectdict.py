from unittest import TestCase

from leryan.types import ObjectDict

class ObjectDictTest(TestCase):

    def test_objectdict_create(self):
        a = ObjectDict()

        a.attribute = 'value'

        self.assertEqual(a.attribute, 'value')
        self.assertEqual(a['attribute'], 'value')

    def test_objectdict_create_from_dict(self):
        a = ObjectDict({'attribute': 'value'})

        self.assertEqual(a.attribute, 'value')
        self.assertEqual(a['attribute'], 'value')

    def test_objectdict_get_method(self):
        a = ObjectDict(
            {
                'attribute1': 'value1',
                'dictattr': {
                    'attribute2': 'value2'
                }
            }
        )

        self.assertEqual(a.get('dontexists', True), True)
        self.assertEqual(a.get('attribute1', 'notthis') ,'value1')

        self.assertEqual(a.dictattr.get('dontexists', True), True)
        self.assertEqual(a.dictattr.get('attribute2', 'notthis'), 'value2')