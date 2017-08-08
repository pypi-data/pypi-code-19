#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Thomas "Cakeisalie5" Touhey <thomas@touhey.fr>
#
# This file is part of the MastodonInstances Python 3.x module.
# MastodonInstances is MIT-licensed.
#******************************************************************************
""" The main API object is defined here.
	It takes the token, and makes multiple operations.
"""

import requests

from .Instance import *
from .Exceptions import *

class Instances:
	def __init__(self, token, *, base = 'https://instances.social/api',
		version = '1.0'):
		""" Initialize the main API object. """

		if not token:
			raise NoTokenError
		if type(token) != str:
			raise TypeError("Token should be a string!")
		if type(version) == float:
			version = str(version)
		if type(version) != str:
			raise TypeError("API version should be a float or string!")
		if type(base) != str:
			raise TypeError("API base should be a string!")

		self.__token = token
		self.__base  = '/'.join((base, version))

	def sample(self, count = 20, *, include_dead = False):
		""" Get a sample count.
			`count`:        the number of instances to get, from 1 to 100.
			`include_dead`: include dead (down for at least two weeks) inst. """

		# Check the user parameters.
		count = int(count)
		count = min(100, max(1, count))
		include_dead = ['false', 'true'][bool(include_dead)]

		# Make the request.
		r = requests.get(self.__base + '/instances/sample',
			params = {'count': str(count), 'include_dead': include_dead},
			headers = {'Authorization': 'Bearer {}'.format(self.__token)})

		if r.status_code == 400:
			raise InvalidTokenError

		return [Instance(data) for data in r.json()['instances']]

	def list(self, count = None, *, start = 0, include_dead = False):
		""" Get the list of instances.
			`count`:        the number of instances to get.
			                0, None and 'all' will return all instances.
			`start`:        ID to start with (growing).
			`include_dead`: include dead (down for at least two weeks) inst.
		"""

		# Check the user parameters.
		count = 0 if count in [0, None, 'all'] else int(count)
		include_dead = ['false', 'true'][bool(include_dead)]
		start = int(start)

		# Make the request.
		r = requests.get(self.__base + '/instances/list',
			params = {'count': str(count), 'include_dead': include_dead,
				'min_id': start},
			headers = {'Authorization': 'Bearer {}'.format(self.__token)})

		if r.status_code == 400:
			raise InvalidTokenError

		return [Instance(data) for data in r.json()['instances']]

	def search(self, query, count = None, *, only_names = False):
		""" Search through instances.
			`query`:      the query (as a string).
			`count`:      the number of instances to get.
			              0, None and 'all' will return all instances.
			`only_names`: only search through names.
		"""

		# Check the user parameters.
		query = str(query)
		count = 0 if count in [0, None, 'all'] else int(count)
		count = str(count)
		only_names = ['false', 'true'][bool(only_names)]

		# Make the request.
		r = requests.get(self.__base + '/instances/search',
			params = {'q': query, 'count': count, 'name': only_names},
			headers = {'Authorization': 'Bearer {}'.format(self.__token)})

		if r.status_code == 400:
			raise InvalidTokenError

		return [Instance(data) for data in r.json()['instances']]

	def get(self, name):
		""" Get details for an instance using its name.
			`name`: the name of the instance to get.
		"""

		# Check the user parameters.
		if type(name) != str:
			raise TypeError("The name should be a string!")

		# Make the request.
		r = requests.get(self.__base + '/instances/show',
			params = {'name': name},
			headers = {'Authorization': 'Bearer {}'.format(self.__token)})

		if r.status_code == 400:
			raise InvalidTokenError
		if r.status_code == 404:
			raise InstanceNotFoundError(name)

		return Instance(r.json())

# End of file.
