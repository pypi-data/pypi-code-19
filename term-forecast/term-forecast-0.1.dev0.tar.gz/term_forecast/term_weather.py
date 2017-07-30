#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Author: KevinMidboe
# @Date:   2017-07-27 21:26:53
# @Last Modified by:   KevinMidboe
# @Last Modified time: 2017-07-30 19:56:18

# TODO LIST
# Get coordinates from IP ✔
# Fetch coordinates from YR ✔
# Convert coordinates to place name w/ google GeoCode api ✔
# Parse return data
# Match weather description to icons ✔
# Check internet connection in a strict way
# Add table for time periode
# Add cache for quicker location for same ip

import fire, json, geoip2.database, ssl, os
from yr.libyr import Yr
from requests import get
from pprint import pprint
from sys import stdout

from emojiParser import EmojiParser
from loadingAnimation import LoadingAnimation


class Location(object):
	def __init__(self):

		abspath = os.path.abspath(__file__)
		dname = os.path.dirname(abspath)
		os.chdir(dname)
		self.reader = geoip2.database.Reader('conf/GeoLite2-City.mmdb')
		self.getIP()

	def getIP(self):
		ip = get('https://api.ipify.org').text
		self.ip = self.reader.city(ip)

	def getCoordinates(self):
		lat = self.ip.location.latitude
		long = self.ip.location.longitude
		return [lat, long]

	def getAreaName(self):
		lat, long = self.getCoordinates()
		coordinates = ','.join([str(lat), str(long)])
		areaURL = 'https://maps.googleapis.com/maps/api/geocode/json?&latlng='

		areaAPIResponse = json.loads(get(areaURL + coordinates).text)
		closestArea = areaAPIResponse['results'][0]['address_components']

		area = {}

		for item in closestArea:
			if 'route' in item['types']:
				area['street'] = item['long_name']

			if 'locality' in item['types']:
				area['town'] = item['long_name']

			if 'administrative_area_level_1' in item['types']:
				area['municipality'] = item['long_name']

			if 'country' in item['types']:
				area['country'] = item['long_name']

		return area


class WeatherForecast(object):
	def __init__(self, area=None):
		# TODO search for area coordinates in a map
		self.area = area

		self.name = None
		self.number = None
		self.variable = None

	def symbolVariables(self, symbol_obj):
		self.name = symbol_obj['@name']
		self.number = symbol_obj['@number']
		self.variable = symbol_obj['@var']

	def parseYrTemperature(self, temperature_obj):
		return temperature_obj['@value'] + ' ' + temperature_obj['@unit']

	def now(self):
		location = Location()
		self.area = location.getAreaName()

		# Create seperate function for formatting
		locationName = '/'.join([self.area['country'], self.area['municipality'], self.area['town'], self.area['street']])

		# Use the defined location name with yr API for location based weather information
		weather = Yr(location_name=locationName)
		now = json.loads(weather.now(as_json=True))


		temperature_output = self.parseYrTemperature(now['temperature'])

		emojiParser = EmojiParser(now['symbol']['@name'])
		weatherIcon_output = emojiParser.convertSematicsToEmoji()

		return ('%s %s' % (temperature_output, weatherIcon_output))


class TermWeather(object):
	def __init__(self):
		print('here')

	# Add now, forecast as args
	def auto(self):
		loadingAnimation = LoadingAnimation()
		loadingAnimation.start()
		weatherForecast = WeatherForecast()
		forecast = weatherForecast.now()
		loadingAnimation.stop()
		stdout.write('\r%s          \n' % forecast)

	def fetch(self, area=None):
		weatherForecast = WeatherForcast(area)
		weatherForecast.now()
		

if __name__ == '__main__':
	ssl._create_default_https_context = ssl._create_unverified_context
	
	fire.Fire(TermWeather())