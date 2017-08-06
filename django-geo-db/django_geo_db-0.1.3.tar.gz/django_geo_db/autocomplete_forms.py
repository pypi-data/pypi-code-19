from django import forms
from dal.autocomplete import ModelSelect2
from django_geo_db.models import UserLocation, City, Location, GeoCoordinate


class UserLocationForm(forms.ModelForm):
    class Meta:
        model = UserLocation
        widgets = {
            'location': ModelSelect2(url='location-autocomplete')
        }
        fields = '__all__'



class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        widgets = {
            'zipcode': ModelSelect2(url='zipcode-autocomplete'),
            'city': ModelSelect2(url='city-autocomplete'),
            'geocoordinate': ModelSelect2(url='geocoordinate-autocomplete'),
            }
        fields = '__all__'




class CityForm(forms.ModelForm):
    class Meta:
        model = City
        widgets = {
            'zipcode': ModelSelect2(url='zipcode-autocomplete'),
            }
        fields = '__all__'

