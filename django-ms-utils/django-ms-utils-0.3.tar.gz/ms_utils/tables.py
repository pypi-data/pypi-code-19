from django.conf import settings
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from django.views.generic import ListView
from django_filters.views import FilterView
from django_filters import FilterSet
from django_tables2 import SingleTableMixin, Table, Column, LinkColumn
from django_tables2.tables import TableBase, DeclarativeColumnsMetaclass
from django_tables2.utils import Accessor


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


class Action:

    template = '<a class="btn btn-xs btn-{kind}" href="{url}">{icon}{text}</a>'
    template_icon = '<i class="fa fa-{icon}"></i> '

    def __init__(self, viewname, text, icon=None, kind='default', args=None, kwargs=None):
        self.viewname = viewname
        self.text = text
        self.icon = icon
        self.kind = kind
        self.args = args
        self.kwargs = kwargs

    def get_icon(self):
        if not self.icon:
            return ''
        return self.template_icon.format(icon=self.icon)

    def get_url(self, record):
        def resolve_if_accessor(val):
            return val.resolve(record) if isinstance(val, Accessor) else val

        params = {}
        if self.args:
            params['args'] = [resolve_if_accessor(a) for a in self.args]

        if self.kwargs:
            params['kwargs'] = {key: resolve_if_accessor(val) for key, val in self.kwargs.items()}

        return reverse(self.viewname, **params)

    def render(self, record):
        data = {
            'url': self.get_url(record),
            'kind': self.kind,
            'icon': self.get_icon(),
            'text': self.text,
        }

        return self.template.format(**data)

class ActionsColumn(Column):
    def __init__(self, columns, *args, **kwargs):
        self.columns = columns
        kwargs['orderable'] = False
        kwargs['verbose_name'] = ''
        kwargs['empty_values'] = ()
        kwargs['attrs'] = dict(td={'class':'col-actions'})
        super().__init__(*args, **kwargs)

    def render(self, **kwargs):
        return mark_safe(' '.join(
            c.render(kwargs['record']) for c in self.columns
        ))
