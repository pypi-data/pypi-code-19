# coding=utf-8
# pylint: disable=missing-docstring


import pytest

from xls_writer import detail


noop_formater_test_data = list(range(10)) + [None, "foo", "bar"]


@pytest.mark.parametrize("value", noop_formater_test_data)
def test_default_formatter(value):
  noop = detail.NoopFormatter()
  assert noop(field=None, instance=value) is value


type_formatter_test_data = (
  (int, "1", 1),
  (int, 1, 1),
  (int, 1.0, 1),
  (float, 1, 1.0),
  (str, 1, "1")
)


@pytest.mark.parametrize("object_type, value, expected", type_formatter_test_data)
def test_default_empty_check(object_type, value, expected):
  check = detail.TypeFormatter(object_type=object_type)
  assert expected == check(field=None, instance=value)
