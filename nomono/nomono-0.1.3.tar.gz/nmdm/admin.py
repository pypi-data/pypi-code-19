from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin

from nmdm import models as mdm_models

@admin.register(mdm_models.City)
class CityAdmin(ModelAdmin):
    fields = ('name',)
    icon = '<i class="material-icons">attachment</i>'

@admin.register(mdm_models.Brand)
class BrandAdmin(ModelAdmin):
    fields = ('name',)
    icon = '<i class="material-icons">attachment</i>'

@admin.register(mdm_models.Hotel)
class HotelAdmin(ModelAdmin):
    fields = ('name', 'stars', 'city')
    icon = '<i class="material-icons">attachment</i>'

@admin.register(mdm_models.Airport)
class AirportAdmin(ModelAdmin):
    fields = ('code', 'city')
    icon = '<i class="material-icons">attachment</i>'


@admin.register(mdm_models.Flight)
class FlightAdmin(ModelAdmin):
    fields = ('name', 'code', 'departure_airport', 'departure_date', 'arrival_airport', 'arrival_date', 'specific_bag_price', 'price')
    icon = '<i class="material-icons">attachment</i>'

@admin.register(mdm_models.Reservation)
class ReservationAdmin(ModelAdmin):
    fields = ('hotel', 'arrival_date', 'duration', 'number_of_pax', 'room_type', 'price')
    icon = '<i class="material-icons">attachment</i>'

@admin.register(mdm_models.Trip)
class TripAdmin(ModelAdmin):
    fields = ('pax', 'reservation', 'inbound_carriers', 'outbound_carriers')
    icon = '<i class="material-icons">attachment</i>'
