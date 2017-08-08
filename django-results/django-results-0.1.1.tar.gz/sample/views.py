from django import forms
from django.shortcuts import render


def form_error_view(request):
    class TestForm(forms.Form):
        required_field = forms.CharField(required=True)

        invalid_field = forms.CharField(max_length=1)

        def clean(self):
            raise forms.ValidationError('non field error happened')

    form = TestForm(data={'invalid_field': 'xxxxx'})

    return render(request, 'results/result.html', context={
        'class': 'danger',
        'title': '这里有一个错误',
        'message': '不知道当讲不当讲，算了我还是讲了',
        'errors': form.errors,
    })
