from __future__ import absolute_import, print_function, unicode_literals

from datetime import date, datetime
from unittest import TestCase

from ngen import validators

NOW = datetime.utcnow()
TODAY = date.today()


class ValidatorTests(TestCase):

    def _tester(self, func, expected_successes, expected_failures):
        for value in expected_successes:
            ret = func(value)
            self.assertEqual(ret, value)

        for value in expected_failures:
            self.assertRaises(
                validators.ValidationError, func, value
            )

    def test_is_int(self):
        self._tester(
            validators.is_int,
            (-1, 0, 1),
            (1., 'bar', [], None, {}, set(), True, (), NOW, TODAY)
        )

    def test_is_float(self):
        self._tester(
            validators.is_float,
            (0., 1.),
            (1, 'bar', [], None, {}, set(), True, (), NOW, TODAY)
        )

    def test_is_number(self):
        self._tester(
            validators.is_number,
            (-1., 0, 1),
            ('bar', [], None, {}, set(), True, (), NOW, TODAY)
        )

    def test_is_char(self):
        self._tester(
            validators.is_char,
            ('bar', ),
            (1., 1, [], None, {}, set(), True, (), NOW, TODAY)
        )

    def test_is_bool(self):
        self._tester(
            validators.is_bool,
            (True, False),
            (1., 'bar', 1, [], None, {}, set(), (), NOW, TODAY)
        )

    def test_is_set(self):
        self._tester(
            validators.is_set,
            (set(), ),
            (1., 'bar', [], None, {}, True, (), NOW, TODAY)
        )

    def test_is_dict(self):
        self._tester(
            validators.is_dict,
            ({}, ),
            (1., 'bar', [], None, set(), True, (), NOW, TODAY)
        )

    def test_is_list(self):
        self._tester(
            validators.is_list,
            ([], ()),
            (1., 'bar', set(), None, {}, True, NOW, TODAY)
        )

    def test_is_datetime(self):
        self._tester(
            validators.is_datetime,
            (NOW, ),
            (1., 'bar', set(), None, {}, True, [], (), TODAY)
        )

    def test_is_date(self):
        self._tester(
            validators.is_date,
            (TODAY, ),
            (1., 'bar', set(), None, {}, True, NOW, [], ())
        )

    def test_check_length(self):

        self.assertRaises(
            validators.ValidationError,
            validators.check_length, 'a', min_length=3
        )

        self.assertRaises(
            validators.ValidationError,
            validators.check_length, 'ab', min_length=3
        )

        expected = 'foo'
        ret = validators.check_length(expected, min_length=3, max_length=5)
        self.assertEqual(ret, expected)

        expected += 'b'
        ret = validators.check_length(expected, min_length=3, max_length=5)
        self.assertEqual(ret, expected)

        expected += 'a'
        ret = validators.check_length(expected, min_length=3, max_length=5)
        self.assertEqual(ret, expected)

        self.assertRaises(
            validators.ValidationError,
            validators.check_length,
            'foobar',
            min_length=3,
            max_length=5
        )
