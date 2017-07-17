from django.utils.safestring import mark_safe
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django_tables2 import Column
from django_tables2.utils import Accessor
from django_tables2.columns import BooleanColumn as BaseBooleanColumn
from django_tables2.columns.base import library


@library.register
class BooleanColumn(BaseBooleanColumn):
    def __init__(self, *args, **kwargs):
        kwargs['yesno'] = (
            mark_safe('<i class="fa fa-check-circle fa-lg text-success"></i>'),
            mark_safe('<i class="fa fa-times-circle fa-lg text-danger"></i>'),
        )
        super().__init__(*args, **kwargs)

    def render(self, value, record, bound_column):
        bool_value = self._get_bool_value(record, value, bound_column)
        if value is None:
            text = mark_safe('<i class="fa fa-question-circle-o fa-lg text-default"></i>')
        else:
            text = self.yesno[int(not bool_value)]
        return text

class RelationColumn(Column):
    def render(self, value):
        return render_to_string('ms_utils/columns/relation.html', dict(items=value.all()))

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
