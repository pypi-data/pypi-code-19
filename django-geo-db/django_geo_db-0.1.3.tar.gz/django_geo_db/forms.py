from django import forms
from django_geo_db.models import UserLocation, City, Location, GeoCoordinate
from django_geo_db.widgets import GeocoordinateWidget


class GeocoordinateForm(forms.ModelForm):
    class Meta:
        model = GeoCoordinate
        fields = [
            'generated_name',
            'lat',
            'lon',
        ]
        widgets = {
            'generated_name': GeocoordinateWidget
        }
