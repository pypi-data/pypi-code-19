#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2017 Thomas "Cakeisalie5" Touhey <thomas@touhey.fr>
#
# This file is part of the MastodonInstances Python 3.x module.
# MastodonInstances is MIT-licensed.
#******************************************************************************
""" Registering utility.
"""

import requests as _requests
from bs4 import BeautifulSoup as _BeautifulSoup

__all__ = ["register"]

def register(application_name, email):
	""" Register an application, get the application ID and the token.
		Those are returned as a tuple: 
		
		app_id, token = register("Hi world", "mail@example.org") """

	r = _requests.post("https://instances.social/api/token",
		data = {'name': application_name, 'email': email})
	if r.status_code != 200:
		raise TokenGatheringError
	text = r.text

	tree = _BeautifulSoup(text, "html5lib")
	body = tree.body.find(True, {'id': 'container-main'}, recursive=True)
	elements = list(body.find('p').children)

	app_id = elements[6]
	token = elements[10].text

	return (app_id, token)

# End of file.
