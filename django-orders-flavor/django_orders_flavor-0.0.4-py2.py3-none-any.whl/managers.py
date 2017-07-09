from django.db import models

from polymorphic.manager import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet


__all__ = ['ItemManager', 'OrderManager']


class BaseItemManager(PolymorphicManager):
    pass


class ItemQuerySet(PolymorphicQuerySet):
    pass


ItemManager = BaseItemManager.from_queryset(ItemQuerySet)


class BaseOrderManager(models.Manager):
    pass


class OrderQuerySet(models.QuerySet):

    def pending(self):
        return self.filter(status=self.model.PENDING)

    def paid(self):
        return self.filter(status=self.model.PAID)


OrderManager = BaseOrderManager.from_queryset(OrderQuerySet)
