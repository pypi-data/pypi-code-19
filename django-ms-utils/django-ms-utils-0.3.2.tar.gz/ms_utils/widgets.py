from django.forms import widgets


class MultiSelectWidget(widgets.SelectMultiple):
    template_name = 'ms_utils/widgets/multiselect.html'

    def __init__(self, *args, **kwargs):
        self.size = 'medium'
        if 'size' in kwargs:
            self.size = kwargs['size']
            del kwargs['size']
        attrs = kwargs.setdefault('attrs', dict())
        attrs['data-role'] = 'multiselect'
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['size'] = self.size
        return context
