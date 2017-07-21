import os
import unittest

import django_settings_helper


class TestDjangoSettingsHelper(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_env(self):

        def assert_object_equal(value1, value2, message=''):
            t2 = type(value2)
            if t2 == list:
                self.assertListEqual(value1, value2, message)
            elif t2 == dict:
                self.assertDictEqual(value1, value2, message)
            else:
                self.assertEqual(value1, value2, message)

        test_cases = [
            # env, eval, type
            ('12', 12, int),
            ('1.23', 1.23, float),
            ('True', True, bool),
            ('False', False, bool),
            ('Yes', True, bool),
            ('No', False, bool),
            ('1', True, bool),
            ('0', False, bool),
            ('On', True, bool),
            ('Off', False, bool),
            ('true', True, bool),
            ('false', False, bool),
            ('test', 'test', str),
            ('{"a": 1, "b": "2"}', {'a': 1, 'b': '2'}, dict),
            ('["a", "b", "c", "d"]', ['a', 'b', 'c', 'd'], list),
            ('{"a":1, "b": [1, 2, 3]}', {'a': 1, 'b': [1, 2, 3]}, 'json'),
        ]

        # prepare test cases
        for idx, case in enumerate(test_cases):
            key = 'TEST_%d' % idx
            val = case[0]
            os.environ.setdefault(key, val)

        # test cases
        for idx, case in enumerate(test_cases):
            test_key = 'TEST_%d' % idx
            eval_val = case[1]
            test_type = case[2]
            test_val = django_settings_helper.get_env(test_key, strict=False, type_cast=test_type)

            assert_object_equal(eval_val, test_val)

        # strict parameter test
        try:
            django_settings_helper.get_env('UNKNOWN_TEST_VALUE', strict=True)
            exception_raised = False
        except django_settings_helper.ImproperlyConfigured:
            exception_raised = True
        self.assertTrue(exception_raised)

        # getting default values
        django_settings_helper.get_env('UNKNOWN_TEST_VALUE', strict=False, default=True, type_cast=bool)

    def test_env_from_file(self):
        """
        test env_from_file
        """
        test_file = os.path.join(os.path.dirname(__file__), 'env_file')
        django_settings_helper.env_from_file(test_file)

        self.assertEqual(
            'Hello, World!',
            django_settings_helper.get_env('TEST_VAR_01', strict=True),
        )

        self.assertEqual(
            'My Value',
            django_settings_helper.get_env('TEST_VAR_02', strict=True),
        )

        self.assertEqual(
            'res#passlikePa!4n',
            django_settings_helper.get_env('secret_key', strict=True),
        )

        self.assertEqual(
            '#QUOTE_#TEST_#VAL',
            django_settings_helper.get_env('quote_test', strict=True),
        )

        self.assertFalse(django_settings_helper.get_env('must_be_skipped_1', strict=False, default=False, type_cast=bool))
        self.assertFalse(django_settings_helper.get_env('must_be_skipped_2', strict=False, default=False, type_cast=bool))

    def test_import_all(self):
        django_settings_helper.import_all('django_settings_helper.test_import', globals())
        # noinspection PyUnresolvedReferences
        self.assertEqual(IMPORT_TEST_VALUE, 'successfully imported!')
