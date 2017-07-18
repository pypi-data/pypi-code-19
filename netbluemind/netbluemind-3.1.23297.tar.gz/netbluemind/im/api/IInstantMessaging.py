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

class IInstantMessaging(BaseEndpoint):
	def __init__(self, apiKey, url ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/im'

	def getLastMessagesBetween (self, user1 , user2 , messagesCount ):
		postUri = "/_getLastMessagesBetween";
		data = None
		queryParams = {  'user1': user1  , 'user2': user2  , 'messagesCount': messagesCount   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.im.api.IMMessage import IMMessage
		from netbluemind.im.api.IMMessage import __IMMessageSerDer__
		return self.handleResult__(serder.ListSerDer(__IMMessageSerDer__()), response)
	def isActiveUser (self, uid ):
		postUri = "/_activeUser/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.BOOLEAN, response)
	def sendGroupChatHistory (self, sender , groupChatId , recipients ):
		postUri = "/_sendGroupChatHistory/{groupChatId}";
		data = None
		postUri = postUri.replace("{groupChatId}",groupChatId);
		data = serder.ListSerDer(serder.STRING).encode(recipients)

		queryParams = {  'sender': sender     };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def setRoster (self, jabberId , data ):
		postUri = "/_setRoster";
		data = None
		data = serder.STRING.encode(data)

		queryParams = {  'jabberId': jabberId    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getRoster (self, jabberId ):
		postUri = "/_getRoster";
		data = None
		queryParams = {  'jabberId': jabberId   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.STRING, response)
