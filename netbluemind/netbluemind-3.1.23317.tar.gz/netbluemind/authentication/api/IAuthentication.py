#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
# 
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
# 
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  See LICENSE.txt
#  END LICENSE
#
import requests
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

class IAuthentication(BaseEndpoint):
	def __init__(self, apiKey, url ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/auth'

	def getCurrentUser (self):
		postUri = "";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.authentication.api.AuthUser import AuthUser
		from netbluemind.authentication.api.AuthUser import __AuthUserSerDer__
		return self.handleResult__(__AuthUserSerDer__(), response)
	def su (self, login ):
		postUri = "/_su";
		data = None
		queryParams = {  'login': login   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.authentication.api.LoginResponse import LoginResponse
		from netbluemind.authentication.api.LoginResponse import __LoginResponseSerDer__
		return self.handleResult__(__LoginResponseSerDer__(), response)
	def ping (self):
		postUri = "/ping";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def login (self, login , password , origin ):
		postUri = "/login";
		data = None
		data = serder.STRING.encode(password)

		queryParams = {  'login': login   , 'origin': origin   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.authentication.api.LoginResponse import LoginResponse
		from netbluemind.authentication.api.LoginResponse import __LoginResponseSerDer__
		return self.handleResult__(__LoginResponseSerDer__(), response)
	def loginWithParams (self, login , password , origin , interactive ):
		postUri = "/loginWithParams";
		data = None
		data = serder.STRING.encode(password)

		queryParams = {  'login': login   , 'origin': origin  , 'interactive': interactive   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.authentication.api.LoginResponse import LoginResponse
		from netbluemind.authentication.api.LoginResponse import __LoginResponseSerDer__
		return self.handleResult__(__LoginResponseSerDer__(), response)
	def logout (self):
		postUri = "/logout";
		data = None
		queryParams = {  };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def validate (self, login , password , origin ):
		postUri = "/validate";
		data = None
		data = serder.STRING.encode(password)

		queryParams = {  'login': login   , 'origin': origin   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.authentication.api.ValidationKind import ValidationKind
		from netbluemind.authentication.api.ValidationKind import __ValidationKindSerDer__
		return self.handleResult__(__ValidationKindSerDer__(), response)
