# coding=utf-8
"""
Implementation details. These classes should be transparent to end user.
"""
import typing

from xls_writer.api import TableField
from . import exceptions, api


# pylint: disable=no-self-use


class EnumeratedFieldEmptyCheck(api.FieldEmptyCheck):
  """
  Checks if field is empty by comparing it to set of known empty values.
  Useful if you have dumb API that, for example, treats -1 as none.
  """

  def __init__(self, empty_values: typing.Sequence):
    self.empty_values = set(empty_values)

  def __call__(self, field: api.TableField, instance) -> bool:
    return instance in self.empty_values


class DefaultFieldEmptyCheck(api.FieldEmptyCheck):
  """
  Field empty check that treats only Nones as empty values.
  """

  def __call__(self, field: api.TableField, instance) -> bool:
    return instance is None


class NoopEmptyCheck(api.FieldEmptyCheck):
  """
  Values are never treated as empty.
  """

  def __call__(self, field: TableField, instance) -> bool:
    return False


class TypeFormatter(api.FieldFormatter):
  """
  Formatter that coalesces to given type. That is: calls ``int(value)``.
  """
  def __init__(self, object_type: type):
    """
    :param object_type: Type to coalesce to.
    """
    self.object_type = object_type

  def __call__(self, field: TableField, instance) -> object:
    return self.object_type(instance)


class NoopFormatter(api.FieldFormatter):
  """
  Formatter that does nothing.
  """

  def __call__(self, field: TableField, instance) -> object:
    return instance


class ConstReader(api.FieldReader):
  """
  Reader that always returns the same value.
  """

  def __init__(self, instance):
    self.instance = instance

  def __call__(self, field: TableField, instance) -> object:
    return self.instance


class DefaultFieldReader(api.FieldReader):
  """
  Field reader that extracts row values by traversing object tree using given path.
  """

  def __init__(self, path: str):
    """
    :param path: Dotted path to field.
    """
    self.path = path.split(".")

  def __get_field(self, inst, fieldname):
    _does_not_exist = object()
    value = getattr(inst, fieldname, _does_not_exist)
    if value is not _does_not_exist:
      return value
    try:
      return inst[fieldname]
    except (KeyError, IndentationError, TypeError):
      pass
    raise exceptions.MissingField()

  def __call__(self, field: TableField, instance) -> object:
    result = instance
    for path_item in self.path:
      try:
        result = self.__get_field(result, path_item)
      except exceptions.MissingField:
        raise exceptions.MissingField(self.path, path_item, instance)
    return result
