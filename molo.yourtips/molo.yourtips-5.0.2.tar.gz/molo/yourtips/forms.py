from django import forms

from molo.yourtips.models import YourTipsEntry


class YourTipsEntryForm(forms.ModelForm):
    tip_text = forms.CharField(widget=forms.Textarea(
    ))

    class Meta:
        model = YourTipsEntry
        fields = [
            "optional_name", 'tip_text', 'allow_share_on_social_media'
        ]
