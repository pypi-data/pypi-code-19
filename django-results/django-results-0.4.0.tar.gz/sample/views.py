from django import forms

from results.views import ResultView


def form_error_view(request):
    class TestForm(forms.Form):
        required_field = forms.CharField(required=True)

        invalid_field = forms.CharField(max_length=1)

        def clean(self):
            raise forms.ValidationError('non field error happened')

    form = TestForm(data={'invalid_field': 'xxxxx'})

    return ResultView.error_view(request, title='这里有一个错误', message='不知道当讲不当讲，算了我还是讲了', error=form.errors)
