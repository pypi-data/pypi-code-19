from django import forms

from unach_photo_server.models import PhotoRepository


class PhotoRepositoryAdminForm(forms.ModelForm):

    class Meta:
        model = PhotoRepository
        fields = '__all__'

    class Media:
        js = ('unach_photo_server/js/type-repo-field-admin.js',)