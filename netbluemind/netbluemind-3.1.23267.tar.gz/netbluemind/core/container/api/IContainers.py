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

class IContainers(BaseEndpoint):
	def __init__(self, apiKey, url ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/containers/_manage'

	def all (self, query ):
		postUri = "/_list";
		data = None
		from netbluemind.core.container.api.ContainerQuery import ContainerQuery
		from netbluemind.core.container.api.ContainerQuery import __ContainerQuerySerDer__
		data = __ContainerQuerySerDer__().encode(query)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
		from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
		return self.handleResult__(serder.ListSerDer(__ContainerDescriptorSerDer__()), response)
	def getContainers (self, containerIds ):
		postUri = "/_mget";
		data = None
		data = serder.ListSerDer(serder.STRING).encode(containerIds)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
		from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
		return self.handleResult__(serder.ListSerDer(__ContainerDescriptorSerDer__()), response)
	def subscribe (self, subject , subscriptions ):
		postUri = "/_subscription/{subject}";
		data = None
		postUri = postUri.replace("{subject}",subject);
		from netbluemind.core.container.api.ContainerSubscription import ContainerSubscription
		from netbluemind.core.container.api.ContainerSubscription import __ContainerSubscriptionSerDer__
		data = serder.ListSerDer(__ContainerSubscriptionSerDer__()).encode(subscriptions)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def setAccessControlList (self, uid , entries ):
		postUri = "/{uid}/_acl";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.core.container.model.acl.AccessControlEntry import AccessControlEntry
		from netbluemind.core.container.model.acl.AccessControlEntry import __AccessControlEntrySerDer__
		data = serder.ListSerDer(__AccessControlEntrySerDer__()).encode(entries)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def update (self, uid , descriptor ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.core.container.model.ContainerModifiableDescriptor import ContainerModifiableDescriptor
		from netbluemind.core.container.model.ContainerModifiableDescriptor import __ContainerModifiableDescriptorSerDer__
		data = __ContainerModifiableDescriptorSerDer__().encode(descriptor)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def allForUser (self, domainUid , userUid , query ):
		postUri = "/_listforuser";
		data = None
		from netbluemind.core.container.api.ContainerQuery import ContainerQuery
		from netbluemind.core.container.api.ContainerQuery import __ContainerQuerySerDer__
		data = __ContainerQuerySerDer__().encode(query)

		queryParams = {  'domainUid': domainUid  , 'userUid': userUid    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
		from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
		return self.handleResult__(serder.ListSerDer(__ContainerDescriptorSerDer__()), response)
	def delete (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def unsubscribe (self, subject , containers ):
		postUri = "/_subscription/{subject}";
		data = None
		postUri = postUri.replace("{subject}",subject);
		data = serder.ListSerDer(serder.STRING).encode(containers)

		queryParams = {    };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def get (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
		from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
		return self.handleResult__(__ContainerDescriptorSerDer__(), response)
	def create (self, uid , descriptor ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
		from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
		data = __ContainerDescriptorSerDer__().encode(descriptor)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def listSubscriptions (self, domain , subject , type ):
		postUri = "/_subscriptions/{subject}@{domain}/{type}";
		data = None
		postUri = postUri.replace("{domain}",domain);
		postUri = postUri.replace("{subject}",subject);
		postUri = postUri.replace("{type}",type);
		queryParams = {     };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
		from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
		return self.handleResult__(serder.ListSerDer(__ContainerDescriptorSerDer__()), response)
	def userSubscriptions (self, domain , subject ):
		postUri = "/_subscriptions/{subject}@{domain}";
		data = None
		postUri = postUri.replace("{domain}",domain);
		postUri = postUri.replace("{subject}",subject);
		queryParams = {    };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
		from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
		return self.handleResult__(serder.ListSerDer(__ContainerDescriptorSerDer__()), response)
	def getIfPresent (self, uid ):
		postUri = "/_ifPresent/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerDescriptor import ContainerDescriptor
		from netbluemind.core.container.model.ContainerDescriptor import __ContainerDescriptorSerDer__
		return self.handleResult__(__ContainerDescriptorSerDer__(), response)
