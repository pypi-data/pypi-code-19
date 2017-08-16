from django import forms

from constrainedfilefield.tests.models import TestModel, TestModelJs, TestModelNoValidate, TestElement


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel
        fields = ['the_file']


class TestModelFormJs(forms.ModelForm):
    class Meta:
        model = TestModelJs
        fields = ['the_file']


class TestModelNoValidateForm(forms.ModelForm):
    class Meta:
        model = TestModelNoValidate
        fields = ['the_file']


class TestElementForm(forms.ModelForm):
    the_file = forms.FileField(required=False, )

    class Meta:
        model = TestElement
        fields = ['the_file']

    def __init__(self, container, *args, **kwargs):
        super(TestElementForm, self).__init__(*args, **kwargs)
        self.container = container
        self.fields['the_file'].validators[0].update_quota(
            items=self.container.test_elements.all(),
            attr_name='the_file',
        )

    def save(self, *args, **kwargs):
        element = super(TestElementForm, self).save(commit=False)
        element.container = self.container
        element.save()


class TestNoModelForm(forms.Form):
    from constrainedfilefield.fields import ConstrainedFileField
    the_file = ConstrainedFileField(null=True,
                                    blank=True,
                                    upload_to='testfile',
                                    content_types=['image/png'],
                                    max_upload_size=10240).formfield()


class TestNoModelJsForm(forms.Form):
    from constrainedfilefield.fields import ConstrainedFileField
    the_file = ConstrainedFileField(null=True,
                                    blank=True,
                                    upload_to='testfile',
                                    content_types=['image/png'],
                                    max_upload_size=10240,
                                    js_checker=True).formfield()
