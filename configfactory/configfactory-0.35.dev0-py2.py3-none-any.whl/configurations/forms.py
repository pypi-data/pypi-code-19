import jsonschema
from django import forms
from django.core.exceptions import ValidationError

from configfactory.configurations import config
from configfactory.exceptions import CircularInjectError, InjectKeyError
from configfactory.forms import JSONFormField
from configfactory.models import Component
from configfactory.utils import inject_dict_params


class ComponentForm(forms.ModelForm):

    class Meta:

        model = Component
        fields = ('name', 'alias', 'require_schema', 'is_global')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'alias': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }


class ComponentSettingsForm(forms.Form):

    def __init__(self, component, environment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.component = component
        self.environment = environment

    settings = JSONFormField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 32,
            'style': 'width: 100%',
        })
    )

    def clean_settings(self):
        data = self.cleaned_data['settings']
        try:
            inject_dict_params(
                data=data,
                params=config.get_all_settings(self.environment, flatten=True),
                flatten=True,
                raise_exception=True
            )
        except (InjectKeyError, CircularInjectError) as e:
            raise ValidationError(str(e))
        if self.component.require_schema:
            try:
                jsonschema.validate(data, self.component.schema)
            except jsonschema.ValidationError as e:
                raise ValidationError(str(e))
        return data


class ComponentSchemaForm(forms.Form):

    schema = JSONFormField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 32,
            'style': 'width: 100%',
        })
    )
