from django import forms
from django.utils.translation import ugettext_lazy as _

from molo.yourtips.models import YourTipsEntry


class YourTipsEntryForm(forms.ModelForm):
    """
    The user submitted entry form class
    """
    tip_text = forms.CharField(widget=forms.Textarea(
    ))

    def clean_tip_text(self):
        data = self.cleaned_data['tip_text']
        if len(data.split()) > 30:
            raise forms.ValidationError(
                _("Sorry your tip is too long, please edit it and cut down"
                  " %d words.") % (len(data.split()) - 30)
            )
        elif len(data) > 140:
            raise forms.ValidationError(
                _("Sorry your tip is too long, please edit it and cut down"
                  " %d characters.") % (len(data) - 140)
            )
        return data

    class Meta:
        model = YourTipsEntry
        fields = [
            "optional_name", 'tip_text', 'allow_share_on_social_media'
        ]
