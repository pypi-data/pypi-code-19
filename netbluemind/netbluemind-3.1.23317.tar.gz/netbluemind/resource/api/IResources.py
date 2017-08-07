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

class IResources(BaseEndpoint):
	def __init__(self, apiKey, url ,domainUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/resources/{domainUid}'
		self.domainUid_ = domainUid
		self.base = self.base.replace('{domainUid}',domainUid)

	def update (self, uid , rd ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.resource.api.ResourceDescriptor import ResourceDescriptor
		from netbluemind.resource.api.ResourceDescriptor import __ResourceDescriptorSerDer__
		data = __ResourceDescriptorSerDer__().encode(rd)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def delete (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getIcon (self, uid ):
		postUri = "/{uid}/icon";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ByteArraySerDer, response)
	def setIcon (self, uid , icon ):
		postUri = "/{uid}/icon";
		data = None
		postUri = postUri.replace("{uid}",uid);
		data = serder.ByteArraySerDer.encode(icon)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def get (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.resource.api.ResourceDescriptor import ResourceDescriptor
		from netbluemind.resource.api.ResourceDescriptor import __ResourceDescriptorSerDer__
		return self.handleResult__(__ResourceDescriptorSerDer__(), response)
	def byEmail (self, email ):
		postUri = "/byEmail/{email}";
		data = None
		postUri = postUri.replace("{email}",email);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.resource.api.ResourceDescriptor import ResourceDescriptor
		from netbluemind.resource.api.ResourceDescriptor import __ResourceDescriptorSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__ResourceDescriptorSerDer__()), response)
	def create (self, uid , rd ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.resource.api.ResourceDescriptor import ResourceDescriptor
		from netbluemind.resource.api.ResourceDescriptor import __ResourceDescriptorSerDer__
		data = __ResourceDescriptorSerDer__().encode(rd)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
