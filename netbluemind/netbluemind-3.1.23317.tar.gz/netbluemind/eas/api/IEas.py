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

class IEas(BaseEndpoint):
	def __init__(self, apiKey, url ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/eas'

	def getHeartbeat (self, deviceUid ):
		postUri = "/_heartbeat";
		data = None
		queryParams = {  'deviceUid': deviceUid   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.eas.api.Heartbeat import Heartbeat
		from netbluemind.eas.api.Heartbeat import __HeartbeatSerDer__
		return self.handleResult__(__HeartbeatSerDer__(), response)
	def setHeartbeat (self, heartbeat ):
		postUri = "/_heartbeat";
		data = None
		from netbluemind.eas.api.Heartbeat import Heartbeat
		from netbluemind.eas.api.Heartbeat import __HeartbeatSerDer__
		data = __HeartbeatSerDer__().encode(heartbeat)

		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getFolderSyncVersions (self, account ):
		postUri = "/_getFolderSync";
		data = None
		from netbluemind.eas.api.Account import Account
		from netbluemind.eas.api.Account import __AccountSerDer__
		data = __AccountSerDer__().encode(account)

		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.MapSerDer(serder.STRING), response)
	def setFolderSyncVersions (self, versions ):
		postUri = "/_setFolderSync";
		data = None
		from netbluemind.eas.api.FolderSyncVersions import FolderSyncVersions
		from netbluemind.eas.api.FolderSyncVersions import __FolderSyncVersionsSerDer__
		data = __FolderSyncVersionsSerDer__().encode(versions)

		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def insertPendingReset (self, account ):
		postUri = "/_reset";
		data = None
		from netbluemind.eas.api.Account import Account
		from netbluemind.eas.api.Account import __AccountSerDer__
		data = __AccountSerDer__().encode(account)

		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getSentItems (self, folderId , account ):
		postUri = "/_getSentItems/{folderId}";
		data = None
		postUri = postUri.replace("{folderId}",folderId);
		from netbluemind.eas.api.Account import Account
		from netbluemind.eas.api.Account import __AccountSerDer__
		data = __AccountSerDer__().encode(account)

		queryParams = {    };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.eas.api.SentItem import SentItem
		from netbluemind.eas.api.SentItem import __SentItemSerDer__
		return self.handleResult__(serder.ListSerDer(__SentItemSerDer__()), response)
	def deletePendingReset (self, folderId , account ):
		postUri = "/_deletePendingReset/{folderId}";
		data = None
		postUri = postUri.replace("{folderId}",folderId);
		from netbluemind.eas.api.Account import Account
		from netbluemind.eas.api.Account import __AccountSerDer__
		data = __AccountSerDer__().encode(account)

		queryParams = {    };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def insertSentItems (self, sentItems ):
		postUri = "/_sentItems";
		data = None
		from netbluemind.eas.api.SentItem import SentItem
		from netbluemind.eas.api.SentItem import __SentItemSerDer__
		data = serder.ListSerDer(__SentItemSerDer__()).encode(sentItems)

		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def needReset (self, folderId , account ):
		postUri = "/_needReset/{folderId}";
		data = None
		postUri = postUri.replace("{folderId}",folderId);
		from netbluemind.eas.api.Account import Account
		from netbluemind.eas.api.Account import __AccountSerDer__
		data = __AccountSerDer__().encode(account)

		queryParams = {    };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.BOOLEAN, response)
	def getConfiguration (self):
		postUri = "/_getConfiguration";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.MapSerDer(serder.STRING), response)
	def isKnownClientId (self, clientId ):
		postUri = "/_sendmailId/{clientId}";
		data = None
		postUri = postUri.replace("{clientId}",clientId);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.BOOLEAN, response)
	def resetSentItems (self, folderId , account ):
		postUri = "/_resetSentItems/{folderId}";
		data = None
		postUri = postUri.replace("{folderId}",folderId);
		from netbluemind.eas.api.Account import Account
		from netbluemind.eas.api.Account import __AccountSerDer__
		data = __AccountSerDer__().encode(account)

		queryParams = {    };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def insertClientId (self, clientId ):
		postUri = "/_sendmailId/{clientId}";
		data = None
		postUri = postUri.replace("{clientId}",clientId);
		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
