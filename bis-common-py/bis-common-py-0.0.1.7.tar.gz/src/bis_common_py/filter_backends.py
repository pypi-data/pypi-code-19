# coding: utf-8
import warnings

from django_filters import compat
from django_filters.rest_framework import DjangoFilterBackend


class FilterBackend(DjangoFilterBackend):
    """
    Переопределен до решения по
    https://github.com/carltongibson/django-filter/pull/742
    """
    def get_schema_fields(self, view):
        # This is not compatible with widgets where the query param differs from the
        # filter's attribute name. Notably, this includes `MultiWidget`, where query
        # params will be of the format `<name>_0`, `<name>_1`, etc...
        assert compat.coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert compat.coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'

        filter_class = getattr(view, 'filter_class', None)
        if filter_class is None:
            try:
                filter_class = self.get_filter_class(view, view.get_queryset())
            except Exception:
                warnings.warn(
                    "{} is not compatible with schema generation".format(
                        view.__class__)
                )
                filter_class = None

        return [] if not filter_class else [
            compat.coreapi.Field(
                name=field_name,
                required=False,
                location='query',
                description=field.label,
                schema=self.get_coreschema_field(field)
            )
            for field_name, field in filter_class.base_filters.items()
        ]