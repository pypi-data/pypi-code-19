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

class IContainerManagement(BaseEndpoint):
	def __init__(self, apiKey, url ,containerUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/containers/_manage/{containerUid}'
		self.containerUid_ = containerUid
		self.base = self.base.replace('{containerUid}',containerUid)

	def getDescriptor (self):
		postUri = "/_descriptor";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
		from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
		return self.handleResult__(__ContainerDescriptorSerDer__(), response)
	def getSettings (self):
		postUri = "/_settings";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.MapSerDer(serder.STRING), response)
	def subscribe (self, subject ):
		postUri = "/_subscription/{subject}";
		data = None
		postUri = postUri.replace("{subject}",subject);
		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getAccessControlList (self):
		postUri = "/_acl";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
		from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
		return self.handleResult__(serder.ListSerDer(__AccessControlEntrySerDer__()), response)
	def getAllItems (self):
		postUri = "/_list";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ItemDescriptor import ItemDescriptor
		from netbluemind.core.container.model.ItemDescriptor import __ItemDescriptorSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemDescriptorSerDer__()), response)
	def subscribers (self):
		postUri = "/_subscription";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ListSerDer(serder.STRING), response)
	def getItemCount (self):
		postUri = "/_itemCount";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.api.Count import Count
		from netbluemind.core.container.api.Count import __CountSerDer__
		return self.handleResult__(__CountSerDer__(), response)
	def setAccessControlList (self, entries ):
		postUri = "/_acl";
		data = None
		from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
		from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
		data = serder.ListSerDer(__AccessControlEntrySerDer__()).encode(entries)

		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def update (self, descriptor ):
		postUri = "/_descriptor";
		data = None
		from netbluemind.core.container.model.ContainerModifiableDescriptor import ContainerModifiableDescriptor
		from netbluemind.core.container.model.ContainerModifiableDescriptor import __ContainerModifiableDescriptorSerDer__
		data = __ContainerModifiableDescriptorSerDer__().encode(descriptor)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def allowOfflineSync (self, subject ):
		postUri = "/{subject}/offlineSync";
		data = None
		postUri = postUri.replace("{subject}",subject);
		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def setSettings (self, settings ):
		postUri = "/_settings";
		data = None
		data = serder.MapSerDer(serder.STRING).encode(settings)

		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getItems (self, uids ):
		postUri = "/_mget";
		data = None
		data = serder.ListSerDer(serder.STRING).encode(uids)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ItemDescriptor import ItemDescriptor
		from netbluemind.core.container.model.ItemDescriptor import __ItemDescriptorSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemDescriptorSerDer__()), response)
	def disallowOfflineSync (self, subject ):
		postUri = "/{subject}/offlineSync";
		data = None
		postUri = postUri.replace("{subject}",subject);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def unsubscribe (self, subject ):
		postUri = "/_subscription/{subject}";
		data = None
		postUri = postUri.replace("{subject}",subject);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def setPersonalSettings (self, settings ):
		postUri = "/_personalSettings";
		data = None
		data = serder.MapSerDer(serder.STRING).encode(settings)

		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
