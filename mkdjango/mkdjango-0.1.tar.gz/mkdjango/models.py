from django.db import models
from django.utils import timezone

__author__ = 'Michael'


class FixedCharField(models.Field):
    def __init__(self, max_length, *args, **kwargs):
        self.__max_length = max_length
        super().__init__(max_length=max_length, *args, **kwargs)

    def db_type(self, connection):
        return "CHAR({})".format(self.__max_length)


class _ManagedDateTimeField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs['auto_now'] = False
        kwargs['auto_now_add'] = False
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if 'auto_now' in kwargs:
            del kwargs['auto_now']
        if 'auto_now_add' in kwargs:
            del kwargs['auto_now_add']
        return name, path, args, kwargs

    def _set_now(self, model_instance):
        value = timezone.now()
        setattr(model_instance, self.attname, value)
        return value


class CreateTimeField(_ManagedDateTimeField):
    """
    创建时间 字段。
    创建时可以手动填入。
    如果创建时为空，则自动填入当前时间。
    """

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if not add:
            return value
        if value is not None:
            return value
        return self._set_now(model_instance)


DELETE_FIELD_NAME = 'is_deleted'


def is_deleted(model_instance):
    return hasattr(model_instance, DELETE_FIELD_NAME) \
           and getattr(model_instance, DELETE_FIELD_NAME)


class ModifyTimeField(_ManagedDateTimeField):
    """
    修改时间 字段。
    创建时可以手动填入。
    修改时自动变为当前时间。
    """

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if add:
            return value
        if is_deleted(model_instance):
            return value
        return self._set_now(model_instance)


class DeleteTimeField(_ManagedDateTimeField):
    """
    删除时间 字段。
    创建时可以手动填入。
    删除时自动变为当前时间。
    """

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if add:
            return value
        if not is_deleted(model_instance):
            # FIXME 如果删除后调用了 save() 方法，则会再次更新删除时间
            # FIXME 不过估计不会有这种操作。。。
            return value
        return self._set_now(model_instance)
