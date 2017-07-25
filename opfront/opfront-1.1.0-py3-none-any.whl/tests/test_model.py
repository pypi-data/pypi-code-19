from opfront.model import Model

from unittest.mock import MagicMock


import unittest


ATTRIBUTE_SET = {
    'hello': 'world',
    'order': 66,
    'test': True,
    'and then there were': None,
}

ID_ATTRIBUTE_SET = {
    **ATTRIBUTE_SET,
    'id': 123
}


class MockResource(object):

    def __init__(self, exists=False):
        self.create = MagicMock()
        self.update = MagicMock()
        self.delete = MagicMock()
        self.exists = MagicMock(return_value=exists)


class TestModel(unittest.TestCase):

    def test_model_adds_attributes_correctly(self):
        m = Model(MagicMock(), **ATTRIBUTE_SET)

        for k, v in ATTRIBUTE_SET.items():
            self.assertEqual(getattr(m, k), v)

    def test_model_serialized_returns_all_required_attributes(self):
        m = Model(MagicMock(), **ATTRIBUTE_SET)

        serialized = m.serialized

        for k, v in ATTRIBUTE_SET.items():
            self.assertEqual(serialized.get(k), v)

    def test_model_serialized_returns_no_extra_attributes(self):
        m = Model(MagicMock(), **ATTRIBUTE_SET)

        serialized = m.serialized

        for k, v in serialized.items():
            self.assertEqual(ATTRIBUTE_SET.get(k), v)

    def test_model_serialized_replaces_submodels_by_model_ids(self):

        full_key = 'nested_model'
        id_key = full_key + '_id'

        nested_attrs = {
            **ATTRIBUTE_SET,
            full_key: Model(MagicMock(), **{'id': 'world'})
        }

        m = Model(MagicMock(), **nested_attrs)
        serialized = m.serialized
        self.assertNotIn(full_key, serialized)
        self.assertIn(id_key, serialized)
        self.assertEqual(serialized[id_key], nested_attrs[full_key].id)

    def test_model_serialized_replaces_list_of_submodels_by_list_of_model_ids(self):
        full_key = 'nested_models'
        id_key = 'nested_model_ids'

        nested_attrs = {
            **ATTRIBUTE_SET,
            full_key: [
                Model(MagicMock(), **{'id': 'hello'}),
                Model(MagicMock(), **{'id': 'world'})
            ]
        }

        model = Model(MagicMock(), **nested_attrs)
        serialized = model.serialized

        self.assertNotIn(full_key, serialized)
        self.assertIn(id_key, serialized)
        self.assertEqual(serialized[id_key], [m.id for m in nested_attrs[full_key]])


class TestModelSave(unittest.TestCase):

    def test_save_without_id_calls_create(self):
        res = MockResource()

        m = Model(res, **ATTRIBUTE_SET)
        m.save()

        self.assertTrue(res.create.called)

    def test_save_without_id_doesnt_call_update(self):
        res = MockResource()

        m = Model(res, **ATTRIBUTE_SET)
        m.save()

        self.assertFalse(res.update.called)

    def test_save_with_id_when_not_exist_calls_create(self):
        res = MockResource()

        m = Model(res, **ID_ATTRIBUTE_SET)
        m.save()

        self.assertTrue(res.create.called)

    def test_save_with_id_when_not_exist_doesnt_call_update(self):
        res = MockResource()

        m = Model(res, **ID_ATTRIBUTE_SET)
        m.save()

        self.assertFalse(res.update.called)

    def test_save_with_id_when_exists_calls_update(self):
        res = MockResource(exists=True)

        m = Model(res, **ID_ATTRIBUTE_SET)
        m.save()

        self.assertTrue(res.update.called)

    def test_save_with_id_when_exists_doesnt_call_create(self):
        res = MockResource(exists=True)

        m = Model(res, **ID_ATTRIBUTE_SET)
        m.save()

        self.assertFalse(res.create.called)


class TestModelDelete(unittest.TestCase):

    def test_delete_without_id_doesnt_call_resource_delete(self):
        res = MockResource()

        m = Model(res, **ATTRIBUTE_SET)
        m.delete()

        self.assertFalse(res.delete.called)

    def test_delete_with_id_calls_resource_delete(self):
        res = MockResource()

        m = Model(res, **ID_ATTRIBUTE_SET)
        m.delete()

        self.assertTrue(res.delete.called)
