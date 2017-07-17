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

class IAddressBooksMgmt(BaseEndpoint):
	def __init__(self, apiKey, url ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/mgmt/addressbooks'

	def backup (self, containerUid , since ):
		postUri = "/{containerUid}/_backupstream";
		data = None
		postUri = postUri.replace("{containerUid}",containerUid);
		queryParams = {   'since': since   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.STREAM, response)
	def reindexDomain (self, domain ):
		postUri = "/_reindexDomain";
		data = None
		queryParams = {  'domain': domain   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def reindex (self, containerUid ):
		postUri = "/{containerUid}/_reindex";
		data = None
		postUri = postUri.replace("{containerUid}",containerUid);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def restore (self, containerUid , restoreStream , reset ):
		postUri = "/{containerUid}/_restorestream";
		data = None
		postUri = postUri.replace("{containerUid}",containerUid);
		data = serder.STREAM.encode(restoreStream)

		queryParams = {    'reset': reset   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def update (self, containerUid , descriptor ):
		postUri = "/{containerUid}";
		data = None
		postUri = postUri.replace("{containerUid}",containerUid);
		from netbluemind.addressbook.api.AddressBookDescriptor import AddressBookDescriptor
		from netbluemind.addressbook.api.AddressBookDescriptor import __AddressBookDescriptorSerDer__
		data = __AddressBookDescriptorSerDer__().encode(descriptor)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def reindexAll (self):
		postUri = "/_reindex";
		data = None
		queryParams = {  };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def delete (self, containerUid ):
		postUri = "/{containerUid}";
		data = None
		postUri = postUri.replace("{containerUid}",containerUid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getComplete (self, containerUid ):
		postUri = "/{containerUid}";
		data = None
		postUri = postUri.replace("{containerUid}",containerUid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.addressbook.api.AddressBookDescriptor import AddressBookDescriptor
		from netbluemind.addressbook.api.AddressBookDescriptor import __AddressBookDescriptorSerDer__
		return self.handleResult__(__AddressBookDescriptorSerDer__(), response)
	def create (self, containerUid , descriptor , isDefault ):
		postUri = "/{containerUid}";
		data = None
		postUri = postUri.replace("{containerUid}",containerUid);
		from netbluemind.addressbook.api.AddressBookDescriptor import AddressBookDescriptor
		from netbluemind.addressbook.api.AddressBookDescriptor import __AddressBookDescriptorSerDer__
		data = __AddressBookDescriptorSerDer__().encode(descriptor)

		queryParams = {    'isDefault': isDefault   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
