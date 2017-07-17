from django.conf import settings
from django.views.generic import ListView
from django.utils.safestring import mark_safe
from django_filters.views import FilterView
from django_filters import FilterSet
from django_tables2 import SingleTableMixin, Table, Column, LinkColumn
from django_tables2.utils import A, Accessor


def check_filter(attrs):
    meta = attrs['Meta']
    if not hasattr(meta, 'fields') and not hasattr(meta, 'exclude'):
        setattr(meta, 'exclude', ['id'])

def check_table(attrs):
    meta = attrs['Meta']
    if not hasattr(meta, 'template'):
        setattr(meta, 'template', 'django_tables2/bootstrap-responsive.html')
    if not hasattr(meta, 'attrs'):
        setattr(meta, 'attrs', {'class':'table table-bordered table-striped'})

def get_attrs(obj, attr):
    attrs = dict()
    if hasattr(obj, attr):
        attrs = dict(getattr(obj, attr).__dict__)
    meta = attrs.setdefault('Meta', type('Meta', (), {}))
    if not hasattr(meta, 'model'):
        setattr(meta, 'model', obj.model)
    return attrs

class TableMixin(SingleTableMixin):
    paginate_by = getattr(settings, 'PAGINATE_BY', 20)

    def get_table_class(self):
        name = type(self).__name__ + 'Table'
        attrs = get_attrs(self, 'Table')
        check_table(attrs)
        cls = type(name, (Table,), attrs)
        return cls

class TableView(TableMixin, ListView):
    template_name = 'ms_utils/list.html'
    model = None

class TableFilterView(TableMixin, FilterView):
    template_name = 'ms_utils/list.html'
    model = None

    def get_filterset_class(self):
        name = type(self).__name__ + 'Filter'
        attrs = get_attrs(self, 'Filter')
        check_filter(attrs)
        cls = type(name, (FilterSet,), attrs)
        return cls
