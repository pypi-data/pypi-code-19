from django.forms.widgets import RendererMixin, Select
from django.utils.html import html_safe
from django.utils.six import python_2_unicode_compatible
from django.template import loader


@html_safe
@python_2_unicode_compatible
class AutocompleteFieldRenderer(object):
    def __init__(self, name, value, attrs, choices):
        self.name = name
        self.value = value
        self.attrs = attrs
        self.choices = choices

    def __iter__(self):
        for idx, choice in enumerate(self.choices):
            yield self.choice_input_class(self.name, self.value, self.attrs.copy(), choice, idx)

    def __str__(self):
        return self.render()

    def render(self):
        return loader.render_to_string('autocomplete_widget/widget.html', {'widget': self})


class AutocompleteSelect(RendererMixin, Select):
    renderer = AutocompleteFieldRenderer
    _empty_value = ''
