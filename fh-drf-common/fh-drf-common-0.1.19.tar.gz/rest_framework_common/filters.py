from rest_framework import exceptions
import django_filters


class EnumFilter(django_filters.filters.BaseInFilter, django_filters.filters.MethodFilter):

    def __init__(self, enum, *args, **kwargs):
        self.enum = enum

        if 'action' not in kwargs:
            kwargs.update(action=self.filter_enum)

        super(EnumFilter, self).__init__(*args, **kwargs)

    def filter_enum(self, queryset, values):
        for k, value in enumerate(values):
            try:
                values[k] = self.enum.get(value).value
            except AttributeError:
                raise exceptions.ValidationError(detail={self.name: ['Invalid']})

        if values:
            filters = {'{}__in'.format(self.name): values}
            return queryset.filter(**filters)
        else:
            return queryset
