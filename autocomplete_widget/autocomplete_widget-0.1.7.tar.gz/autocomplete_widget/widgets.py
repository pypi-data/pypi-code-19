from django.forms.widgets import Widget


class AutocompleteSelect(Widget):
    template_name = 'autocomplete_widget/widget.html'

    def __init__(self, attrs=None, choices=()):
        super(AutocompleteSelect, self).__init__(attrs)
        self.choices = list(choices)

    def get_context(self, name, value, attrs):
        context = {}
        context['widget'] = self
        return context
