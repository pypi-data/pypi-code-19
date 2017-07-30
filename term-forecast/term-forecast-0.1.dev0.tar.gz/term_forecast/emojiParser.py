#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# @Author: KevinMidboe
# @Date:   2017-07-29 11:56:24
# @Last Modified by:   KevinMidboe
# @Last Modified time: 2017-07-30 13:17:19

from fuzzywuzzy import process

# Find the first word, if it is a noun or a adjective. ✔️
# Remove the adjective and split if there is a AND ✔️
# Then match the first noun to list and add that emoji ✔️
# and then match the second to list and add that emoji ✔️
# REGEX this bitch up 

symbol_table = {
	'clear sky': '☀️',
	'fair': '🌤',
	'partly cloudy': '⛅️',
	'cloudy': ' ☁️ ',
	'thunder': '⚡️',
	
	'rain showers': '🌦',
	'rain': '🌧',
	'sleet showers': '🌦 💦',
	'sleet': '🌨 💦',
	'snow showers': '⛅ ❄️',
	'snow': '🌨',

	'rain': '🌧',
	'sleet': '🌧',
	'snow': '🌨',

	'showers': '🌤'
	}

severity = {
		'rain': ['', ' ☂️', ' ☔️'],
		'sleet': [' 💦 ', ' 💧 ', ' 💧 💦 '],
		'snow': [' ❄️ ', ' ❄️ ❄️ ', ' ❄️ ❄️ ❄️ ']
		}

class EmojiParser(object):
	def __init__(self, condition_text):
		self.condition_expression = condition_text.lower()
		self.severity = None
		self.nouns = []

		self.weather_nouns = ['cleary sky', 'fair', 'cloudy', 'rain', 'rain showers', 'sleet',
			'sleet showers', 'snow showers', 'thunder', 'snow']
		self.weather_adjectives = {'light': 0, 'normal': 1, 'heavy': 2}

	def __str__(self):
	 	return str([self.condition_expression, self.severity, self.nouns])

	# Splits and lowers the condition text for easier parsing
	def splitCondition(self, condition):
		return condition.split()

	# Takes a input or uses condition_expression to find adjective in sentence
	def findAdjective(self, sentence=None):
		if sentence is None:
			sentence = self.condition_expression

		# Splits and iterates over each word in sentence
		expression = self.splitCondition(sentence)
		for word in expression:
			if word in self.weather_adjectives:
				# Return the word if matched with weather_adjectives
				return word

		return None

	# Removes the first adjective in the a given sentence
	def removeAdjective(self):
		adjective = self.findAdjective()
		if adjective:	# Adjective is not None
			expression = self.splitCondition(self.condition_expression)
			expression.remove(adjective)
			return ' '.join(expression)
		else:
			return self.condition_expression


	def severityValue(self):
		adjective = self.findAdjective()

		if adjective:
			self.severity = self.weather_adjectives[adjective]
		else:
			self.severity = self.weather_adjectives['normal']

	def findWeatherTokens(self):
		# If present removes the leading adjective
		sentence = self.removeAdjective()
		
		# If multiple tokens/weather_nouns split all between the 'and'
		if 'and' in sentence:
			self.nouns = sentence.split(' and ')
		else:
			self.nouns = [sentence]


	# Use the symbol_table to convert the forecast name to emoji
	def emojify(self, noun):
		return symbol_table[noun]

	# Does as emojify above, but iterates over a list if multiple elements
	def emojifyList(self, noun_list):
		returnList = []
		
		# TODO use more like a map function?
		for noun in noun_list:
			returnList.append(self.emojify(noun))

		return '  '.join(returnList)

	def findPrimaryForecast(self):
		# Copies the contents not the refrence to the list
		noun_list = list(self.nouns)
		forecast = noun_list.pop(0)

		# Translates to emoji once here instead of twice below
		forecast_emoji = self.emojify(forecast)

		if forecast in severity:
			return ('%s %s' % (forecast_emoji, severity[forecast]))
		else:
			return forecast_emoji


	# Trying to analyze the semantics of the condition text
	def emojifyWeatherForecast(self):
		# Finds the tokens/nouns of weather for the given input text and severity value
		self.findWeatherTokens()
		self.severityValue()

		primary_forecast = self.findPrimaryForecast()
		secondary_forecast = self.emojifyList(self.nouns[1:])
		
		return ('%s %s' % (primary_forecast, secondary_forecast))


	def convertSematicsToEmoji(self):
		return self.emojifyWeatherForecast()


def main():
	emojiParser = EmojiParser('Cloudy')
	print(emojiParser.convertSematicsToEmoji())


if __name__ == '__main__':
	main()