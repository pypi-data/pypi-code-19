# coding: utf-8
from django_filters import CharFilter


class FieldFiler(CharFilter):
    """
    Специальный фильтр для поля, которое позволяет задавать список отображаемых
    в выводе сервиса полей объекта
    """
    def filter(self, qs, value):
        # Не изменяем qs
        return qs
