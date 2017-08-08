#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Thomas "Cakeisalie5" Touhey <thomas@touhey.fr>
#
# This file is part of the MastodonInstances Python 3.x module.
# MastodonInstances is MIT-licensed.
#******************************************************************************
""" The MastodonInstances exceptions.
	Those are the one getting raised here!
"""

class NoTokenError(Exception):
	def __init__(self):
		msg = "Token shouldn't be empty, get yours at:\n" \
			"> https://instances.social/api/token"
		super(NoTokenError, self).__init__(msg)

class InvalidTokenError(Exception):
	def __init__(self):
		msg = "Invalid token!"
		super(InvalidTokenError, self).__init__(msg)

class InstanceNotFoundError(Exception):
	def __init__(self, name):
		msg = "Instance '{}' was not found!".format(name)
		super(InstanceNotFoundError, self).__init__(msg)

class TokenGatheringError(Exception):
	def __init__(self):
		msg = "Token could not be gathered!"
		super(TokenGatheringError, self).__init__(msg)

# End of file.
