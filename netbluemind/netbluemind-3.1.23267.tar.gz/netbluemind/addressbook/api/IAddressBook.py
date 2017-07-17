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

class IAddressBook(BaseEndpoint):
	def __init__(self, apiKey, url ,containerUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/addressbooks/{containerUid}'
		self.containerUid_ = containerUid
		self.base = self.base.replace('{containerUid}',containerUid)

	def getPhoto (self, uid ):
		postUri = "/{uid}/photo";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ByteArraySerDer, response)
	def allUids (self):
		postUri = "";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ListSerDer(serder.STRING), response)
	def update (self, uid , card ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.addressbook.api.VCard import VCard
		from netbluemind.addressbook.api.VCard import __VCardSerDer__
		data = __VCardSerDer__().encode(card)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def updates (self, changes ):
		postUri = "/_mupdates";
		data = None
		from netbluemind.addressbook.api.VCardChanges import VCardChanges
		from netbluemind.addressbook.api.VCardChanges import __VCardChangesSerDer__
		data = __VCardChangesSerDer__().encode(changes)

		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerUpdatesResult import ContainerUpdatesResult
		from netbluemind.core.container.model.ContainerUpdatesResult import __ContainerUpdatesResultSerDer__
		return self.handleResult__(__ContainerUpdatesResultSerDer__(), response)
	def delete (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def deletePhoto (self, uid ):
		postUri = "/{uid}/photo";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def changeset (self, since ):
		postUri = "/_changeset";
		data = None
		queryParams = {  'since': since   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
		from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
		return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
	def changesetById (self, since ):
		postUri = "/_changesetById";
		data = None
		queryParams = {  'since': since   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
		from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
		return self.handleResult__(__ContainerChangesetSerDer__(serder.LONG), response)
	def search (self, query ):
		postUri = "/_search";
		data = None
		from netbluemind.addressbook.api.VCardQuery import VCardQuery
		from netbluemind.addressbook.api.VCardQuery import __VCardQuerySerDer__
		data = __VCardQuerySerDer__().encode(query)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.addressbook.api.VCardInfo import VCardInfo
		from netbluemind.addressbook.api.VCardInfo import __VCardInfoSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		from netbluemind.core.api.ListResult import ListResult
		from netbluemind.core.api.ListResult import __ListResultSerDer__
		return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__VCardInfoSerDer__())), response)
	def create (self, uid , card ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.addressbook.api.VCard import VCard
		from netbluemind.addressbook.api.VCard import __VCardSerDer__
		data = __VCardSerDer__().encode(card)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def copy (self, uids , destContainerUid ):
		postUri = "/_copy/{destContainerUid}";
		data = None
		data = serder.ListSerDer(serder.STRING).encode(uids)

		postUri = postUri.replace("{destContainerUid}",destContainerUid);
		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getVersion (self):
		postUri = "/_version";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.LONG, response)
	def move (self, uids , destContainerUid ):
		postUri = "/_move/{destContainerUid}";
		data = None
		data = serder.ListSerDer(serder.STRING).encode(uids)

		postUri = postUri.replace("{destContainerUid}",destContainerUid);
		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def multipleGet (self, uids ):
		postUri = "/_mget";
		data = None
		data = serder.ListSerDer(serder.STRING).encode(uids)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.addressbook.api.VCard import VCard
		from netbluemind.addressbook.api.VCard import __VCardSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__VCardSerDer__())), response)
	def getInfo (self, uid ):
		postUri = "/{uid}/info";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.addressbook.api.VCardInfo import VCardInfo
		from netbluemind.addressbook.api.VCardInfo import __VCardInfoSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__VCardInfoSerDer__()), response)
	def sync (self, since , changes ):
		postUri = "/_sync";
		data = None
		from netbluemind.addressbook.api.VCardChanges import VCardChanges
		from netbluemind.addressbook.api.VCardChanges import __VCardChangesSerDer__
		data = __VCardChangesSerDer__().encode(changes)

		queryParams = {  'since': since    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
		from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
		return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
	def itemChangelog (self, uid , arg1 ):
		postUri = "/{uid}/_itemchangelog";
		data = None
		postUri = postUri.replace("{uid}",uid);
		data = serder.LONG.encode(arg1)

		queryParams = {    };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ItemChangelog import ItemChangelog
		from netbluemind.core.container.model.ItemChangelog import __ItemChangelogSerDer__
		return self.handleResult__(__ItemChangelogSerDer__(), response)
	def getIcon (self, uid ):
		postUri = "/{uid}/icon";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ByteArraySerDer, response)
	def getComplete (self, uid ):
		postUri = "/{uid}/complete";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.addressbook.api.VCard import VCard
		from netbluemind.addressbook.api.VCard import __VCardSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__VCardSerDer__()), response)
	def containerChangelog (self, arg0 ):
		postUri = "/_changelog";
		data = None
		data = serder.LONG.encode(arg0)

		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerChangelog import ContainerChangelog
		from netbluemind.core.container.model.ContainerChangelog import __ContainerChangelogSerDer__
		return self.handleResult__(__ContainerChangelogSerDer__(), response)
	def setPhoto (self, uid , photo ):
		postUri = "/{uid}/photo";
		data = None
		postUri = postUri.replace("{uid}",uid);
		data = serder.ByteArraySerDer.encode(photo)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def reset (self):
		postUri = "/_reset";
		data = None
		queryParams = {  };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def createById (self, id , card ):
		postUri = "/_byId";
		data = None
		from netbluemind.addressbook.api.VCard import VCard
		from netbluemind.addressbook.api.VCard import __VCardSerDer__
		data = __VCardSerDer__().encode(card)

		queryParams = {  'id': id    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def collect (self, card ):
		postUri = "/_collect";
		data = None
		from netbluemind.addressbook.api.VCard import VCard
		from netbluemind.addressbook.api.VCard import __VCardSerDer__
		data = __VCardSerDer__().encode(card)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.STRING, response)
