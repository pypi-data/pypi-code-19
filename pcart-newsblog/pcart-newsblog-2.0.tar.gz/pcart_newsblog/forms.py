from django import forms
from .models import ArticleBlockPluginModel


class ArticleBlockPluginForm(forms.ModelForm):
    model = ArticleBlockPluginModel

    class Meta:
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(ArticleBlockPluginForm, self).__init__(*args, **kwargs)
    #     self.fields['template_name'] = forms.ChoiceField(
    #         label=_('Template name'),
    #     )
