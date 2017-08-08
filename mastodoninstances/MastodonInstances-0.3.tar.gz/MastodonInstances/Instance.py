#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Thomas "Cakeisalie5" Touhey <thomas@touhey.fr>
#
# This file is part of the MastodonInstances Python 3.x module.
# MastodonInstances is MIT-licensed.
#******************************************************************************
""" Wrapper around the instance object.
	Serves for treating the data, and stuff.
"""

import dateutil.parser as _dateparse

__all__ = ["Instance"]

class Rank:
	""" A rank object, with scores and rank. """

	def __init__(self, score, rank):
		""" Rank object initializer. """

		self.score = score
		self.rank = rank

	def __repr__(self):
		""" Represent the rank object. """

		return "<Rank (Score={}, Rank={})>".format(self.score, self.rank)

class Prohibited:
	""" The prohibited object, which tells the prohibited status of various
		elements recognized by the API. """

	__props = [('Nudity (CW)', 'nudity_cw'), ('Nudity (No CW)', 'nudity_nocw'),
		('Porn (CW)', 'porn_cw'), ('Porn (No CW)', 'porn_nocw'),
		('Sexism', 'sexism'), ('Racism', 'racism'),
		('Illegal content links', 'illegal'), ('Spam', 'spam'),
		('Advertising', 'ads'), ('Hate', 'hate'),
		('Harassment', 'harassment'), ('Spoilers (No CW)', 'spoilers_nocw')]

	def __init__(self, el):
		""" Initialize a prohibited object out of a list with the prohibited
			codes. """

		self.nudity_cw     = 'nudity_all' in el
		self.nudity_nocw   = 'nudity_all' in el or 'nudity_nocw' in el
		self.porn_cw       = 'pornography_all' in el
		self.porn_nocw     = 'pornography_all' in el \
			or 'pornography_nocw' in el
		self.sexism        = 'sexism' in el
		self.racism        = 'racism' in el
		self.illegal       = 'illegalContentLinks' in el
		self.spam          = 'spam' in el
		self.ads           = 'advertising' in el
		self.hate          = 'hateSpeeches' in el
		self.harassment    = 'harassment' in el
		self.spoilers_nocw = 'spoilers_nocw' in el

	def __iter__(self):
		""" Iterate on the properties. """

		for name, prop in self.__props:
			yield (name, self.__getattribute__(prop))

	def __repr__(self):
		""" Represent the Prohibited object. """

		rep = '<Prohibited (' + ', '.join('{}: {}'.format(name,
			value) for name, value in self) + '>'
		return rep

class Instance:
	""" The main instance class.
		Regroups all of the information for a Mastodon Instance. """

	__props = [('ID', 'id'), ('Name', 'name'), ('Version', 'version'),
		('Open registrations', 'open'), ('Short description', 'shortdesc'),
		('Full description', 'fulldesc'), ('Topic', 'topic'),
		('Languages', 'lang'), ('Other languages are accepted', 'otherlang'),
		('Federates with', 'federates_with'), ('Prohibited', 'prohibited'),
		('Added at', 'added'), ('Checked at', 'checked'),
		('Updated at', 'updated'), ('Uptime', 'uptime'), ('Is up', 'up'),
		('Is dead', 'dead'), ('IPv6', 'ipv6'), ('HTTPS Rank', 'https'),
		('OBS Rank', 'obs'), ('User count', 'users'),
		('Statuses count', 'statuses'), ('Connections count', 'connections')]

	def __init__(self, json):
		""" Initialize an Instance object. """

		self.id      = json['id']
		self.name    = json['name']
		self.version = json['version']
		self.open    = json['open_registrations']

		# Information.
		self.shortdesc      = None
		self.fulldesc       = None
		self.topic          = None
		self.lang           = []
		self.otherlang      = False
		self.federates_with = 'all'
		self.prohibited     = Prohibited([])
		if json['info']:
			info = json['info']

			self.shortdesc      = info['short_description']
			self.fulldesc       = info['full_description']
			self.topic          = info['topic']
			self.lang           = info['languages']
			self.otherlang      = info['other_languages_accepted']
			self.federates_with = info['federates_with']
			self.prohibited     = Prohibited(info['prohibited_content'])

		# Dates.
		try:    self.added   = _dateparse.parser.parse(json['added_at'])
		except: self.added   = None
		try:    self.updated = _dateparse.parser.parse(json['updated_at'])
		except: self.updated = None
		try:    self.checked = _dateparse.parser.parse(json['checked_at'])
		except: self.checked = None

		# Statistics.
		self.uptime  = 1 if not json['uptime'] else float(json['uptime'])
		self.up      = json['up'] if json['up'] else False
		self.dead    = json['dead'] if json['dead'] else False
		self.ipv6    = json['ipv6'] if json['ipv6'] else False

		self.users = json['users']
		self.statuses = json['statuses']
		self.connections = json['connections']

		# Ranks.
		self.https = None
		self.obs   = None
		if json['https_score'] != None:
			self.https = Rank(json['https_score'], json['https_rank'])
		if json['obs_score'] != None:
			self.obs = Rank(json['obs_score'], json['obs_rank'])

	def __iter__(self):
		""" Iterate on a Mastodon Instance object to get the properties
			and their values. """

		for name, prop in self.__props:
			yield (name, self.__getattribute__(prop))

	def __repr__(self):
		rep = "<Mastodon Instance '{}'>".format(self.name)
		return rep

# End of file.
