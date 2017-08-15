from django.forms.widgets import Widget


class SelectWidget(Widget):
    def __init__(self, attrs=None, choices=()):
        super(SelectWidget, self).__init__(attrs)
        self.choices = list(choices)

    def get_context(self, name, value, attrs):
        context = {}
        context['widget'] = self
        context['name'] = name
        context['value'] = value
        context['attrs'] = attrs
        return context

    @property
    def choices_toggled(self):
        for k, v in self.choices:
            yield (k, v, k in self.values)


class AutocompleteSelect(SelectWidget):
    template_name = 'djangowidgets/autocompleteselect.html'


class ButtonSelect(SelectWidget):
    template_name = 'djangowidgets/buttonselect.html'

    def get_context(self, name, value, attrs):
        context = super(ButtonSelect, self).get_context(name, value, attrs)
        context['select_multiple'] = False
        self.values = [value]
        return context


class ButtonSelectMultiple(SelectWidget):
    template_name = 'djangowidgets/buttonselect.html'

    def get_context(self, name, value, attrs):
        context = super(ButtonSelectMultiple, self).get_context(name, value, attrs)
        context['select_multiple'] = True
        self.values = value.split(',')
        return context
