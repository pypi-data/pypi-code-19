from __future__ import unicode_literals

import requests
import scrapy
from bs4 import BeautifulSoup
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.conf.global_settings import LANGUAGES

# Create your models here.
from lxml import html

RYANAIR_HOLIDAYS_BRANDS = [
    ('UK', 'United Kingdom'),
    ('D','Deutschland'),
    ('IR', 'Ireland'),
    ('ES', 'España'),
    ('IT', 'Italia')
]


RYANAIR_HOLIDAYS_LANGUAGES = [
    ('eng', 'English')
]


class Brand(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

class Hotel(models.Model):
    name = models.CharField(max_length=250)
    stars = models.IntegerField()
    city = models.ForeignKey(City, related_name='city_hotel')

    def __str__(self):
        return self.name

class Airport(models.Model):
    code = models.CharField(max_length=250)
    city = models.ForeignKey(City, related_name='city_airport')

    def __str__(self):
        return '%s[%s]' % (self.city, self.code)

class Flight(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=20)
    departure_airport = models.ForeignKey(Airport, related_name='departure')
    departure_date = models.DateTimeField()
    arrival_airport = models.ForeignKey(Airport, related_name='arrival')
    arrival_date = models.DateTimeField()
    specific_bag_price = models.FloatField()
    price = models.FloatField(default=1.00)

    def __str__(self):
        return '%s:%s - %s:%s' % (str(self.departure_airport), self.departure_date, str(self.arrival_airport), self.arrival_date)


class Reservation(models.Model):
    hotel = models.ForeignKey(Hotel)
    arrival_date = models.DateTimeField()
    duration = models.IntegerField()
    number_of_pax = models.IntegerField()
    room_type = models.CharField(max_length=250)
    price = models.FloatField(default=1.00)

    def __str__(self):
        return '%s:%s' % (self.hotel.name, self.arrival_date)


class Price(models.Model):
    org = models.ForeignKey(Brand)
    value = models.FloatField(default=1.00)


class ComparisonRecord(models.Model):
    subject = models.ForeignKey(Brand)
    prices = models.ManyToManyField(Price)

    @property
    def subject_price(self):
        return Price.objects.get(org=self.subject).value


class Trip(models.Model):
    pax = models.IntegerField(default=1)
    reservation = models.ForeignKey(Reservation)
    inbound_carriers = models.ManyToManyField(Flight, related_name='inbound')
    outbound_carriers = models.ManyToManyField(Flight, related_name='outbound')

    def __str__(self):
        return 'Trip #%s' % self.pk

# ===========================================================================================================================
# class NamedEntity(models.Model):
#     name = models.CharField(max_length=1000, blank=False, null=False)
#
#
# class Supplier(NamedEntity):
#     url = models.CharField(max_length=1000, blank=False, null=False)
#     is_flight = models.BooleanField(default=False, blank=False, null=False)
#
#     class Meta:
#         verbose_name = _('supplier')
#         verbose_name_plural = _('suppliers')
#         ordering = ['name']
#
#     def __str__(self):
#         return self.name
#
#
# class Brand(NamedEntity):
#     locale = models.CharField(max_length=10, blank=False, null=False, choices=LANGUAGES)
#     suppliers = models.ManyToManyField(Supplier, related_name='brands')
#
#     def __str__(self):
#         return 'Brand %s' % (self.pk)
#
#     class Meta:
#         verbose_name = _('brand')
#         verbose_name_plural = _('brands')
#         ordering = ['pk']
#
#
# class Customer(NamedEntity):
#     code = models.CharField(max_length=250)
#     url = models.CharField(max_length=1000, blank=False, null=False)
#     suppliers = models.ManyToManyField(Brand, related_name='clients')
#
#     class Meta:
#         verbose_name = _('customer')
#         verbose_name_plural = _('customers')
#         ordering = ['pk']
#
#     def __str__(self):
#         return 'Customer %s' % (self.pk)
#
#
# class Search(models.Model):
#     client = models.ForeignKey(Customer)
#     brand = models.ForeignKey(Brand)
#
#     class Meta:
#         verbose_name = _('search')
#         verbose_name_plural = _('searches')
#         ordering = ['id']
#
#     def __str__(self):
#         return 'Search %s' % (self.pk)
#
#
# class Property(models.Model):
#     dom_query = models.CharField(max_length=250)
#     query_param = models.CharField(max_length=250)
#     display_name = models.CharField(max_length=250)
#     search = models.ForeignKey(Search, related_name='properties')
#
#     class Meta:
#         verbose_name = _('property')
#         verbose_name_plural = _('properties')
#         ordering = ['pk']
#
#     def __str__(self):
#         return self.display_name
#
#
# class Portal(models.Model):
#     url = models.CharField(max_length=250)
#
#     def collect_data(self):
#         page = requests.get(self.url)
#         tree = html.fromstring(page.content)
#         return tree
#
#
# class ReadAction(models.Model):
#     dom_query = models.CharField(max_length=250)
#
#     def scrape(self, tree):
#         data = tree.xpath(self.dom_query)
#         return data
#
#
# class BlogSpider(scrapy.Spider):
#     name = 'ryanairspider'
#     start_urls = ['https://blog.scrapinghub.com']
#
#     def parse(self, response):
#         for title in response.css('h2.entry-title'):
#             yield {'title': title.css('a ::text').extract_first()}
#
#         for next_page in response.css('div.prev-post > a'):
#             yield response.follow(next_page, self.parse)