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

class IDevice(BaseEndpoint):
	def __init__(self, apiKey, url ,userUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/devices/{userUid}'
		self.userUid_ = userUid
		self.base = self.base.replace('{userUid}',userUid)

	def setPartnership (self, uid ):
		postUri = "/{uid}/_partnership";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def deleteAll (self):
		postUri = "/_deleteAll";
		data = None
		queryParams = {  };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def update (self, uid , device ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.device.api.Device import Device
		from netbluemind.device.api.Device import __DeviceSerDer__
		data = __DeviceSerDer__().encode(device)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def list (self):
		postUri = "/_list";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.device.api.Device import Device
		from netbluemind.device.api.Device import __DeviceSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		from netbluemind.core.api.ListResult import ListResult
		from netbluemind.core.api.ListResult import __ListResultSerDer__
		return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__DeviceSerDer__())), response)
	def unwipe (self, uid ):
		postUri = "/_unwipe/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def delete (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def unsetPartnership (self, uid ):
		postUri = "/{uid}/_partnership";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getComplete (self, uid ):
		postUri = "/{uid}/complete";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.device.api.Device import Device
		from netbluemind.device.api.Device import __DeviceSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__DeviceSerDer__()), response)
	def wipe (self, uid ):
		postUri = "/_wipe/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def byIdentifier (self, identifier ):
		postUri = "/{identifier}/byIdentifier";
		data = None
		postUri = postUri.replace("{identifier}",identifier);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.device.api.Device import Device
		from netbluemind.device.api.Device import __DeviceSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__DeviceSerDer__()), response)
	def create (self, uid , device ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.device.api.Device import Device
		from netbluemind.device.api.Device import __DeviceSerDer__
		data = __DeviceSerDer__().encode(device)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def updateLastSync (self, uid ):
		postUri = "/{uid}/_lastSync";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
