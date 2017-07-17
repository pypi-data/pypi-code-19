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

class IGroup(BaseEndpoint):
	def __init__(self, apiKey, url ,domainUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/groups/{domainUid}'
		self.domainUid_ = domainUid
		self.base = self.base.replace('{domainUid}',domainUid)

	def allUids (self):
		postUri = "/_alluids";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ListSerDer(serder.STRING), response)
	def update (self, uid , group ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.group.api.Group import Group
		from netbluemind.group.api.Group import __GroupSerDer__
		data = __GroupSerDer__().encode(group)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def byName (self, name ):
		postUri = "/byName/{name}";
		data = None
		postUri = postUri.replace("{name}",name);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.group.api.Group import Group
		from netbluemind.group.api.Group import __GroupSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__GroupSerDer__()), response)
	def delete (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def remove (self, uid , members ):
		postUri = "/{uid}/members";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.group.api.Member import Member
		from netbluemind.group.api.Member import __MemberSerDer__
		data = serder.ListSerDer(__MemberSerDer__()).encode(members)

		queryParams = {    };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getParents (self, uid ):
		postUri = "/{uid}/parents";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.group.api.Group import Group
		from netbluemind.group.api.Group import __GroupSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__GroupSerDer__())), response)
	def search (self, query ):
		postUri = "/_search";
		data = None
		from netbluemind.group.api.GroupSearchQuery import GroupSearchQuery
		from netbluemind.group.api.GroupSearchQuery import __GroupSearchQuerySerDer__
		data = __GroupSearchQuerySerDer__().encode(query)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.group.api.Group import Group
		from netbluemind.group.api.Group import __GroupSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__GroupSerDer__())), response)
	def byEmail (self, email ):
		postUri = "/byEmail/{email}";
		data = None
		postUri = postUri.replace("{email}",email);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.group.api.Group import Group
		from netbluemind.group.api.Group import __GroupSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__GroupSerDer__()), response)
	def create (self, uid , group ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.group.api.Group import Group
		from netbluemind.group.api.Group import __GroupSerDer__
		data = __GroupSerDer__().encode(group)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def setRoles (self, uid , roles ):
		postUri = "/{uid}/roles";
		data = None
		postUri = postUri.replace("{uid}",uid);
		data = serder.SetSerDer(serder.STRING).encode(roles)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getExpandedUsersMembers (self, uid ):
		postUri = "/{uid}/expandedusersmembers";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.group.api.Member import Member
		from netbluemind.group.api.Member import __MemberSerDer__
		return self.handleResult__(serder.ListSerDer(__MemberSerDer__()), response)
	def getRoles (self, uid ):
		postUri = "/{uid}/roles";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.SetSerDer(serder.STRING), response)
	def add (self, uid , members ):
		postUri = "/{uid}/members";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.group.api.Member import Member
		from netbluemind.group.api.Member import __MemberSerDer__
		data = serder.ListSerDer(__MemberSerDer__()).encode(members)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getByExtId (self, extid ):
		postUri = "/_extid/{extid}";
		data = None
		postUri = postUri.replace("{extid}",extid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.group.api.Group import Group
		from netbluemind.group.api.Group import __GroupSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__GroupSerDer__()), response)
	def touch (self, uid ):
		postUri = "/{uid}/_touch";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getComplete (self, uid ):
		postUri = "/{uid}/complete";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.group.api.Group import Group
		from netbluemind.group.api.Group import __GroupSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__GroupSerDer__()), response)
	def getGroupsWithRoles (self, roles ):
		postUri = "/_rolegroups";
		data = None
		data = serder.ListSerDer(serder.STRING).encode(roles)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.SetSerDer(serder.STRING), response)
	def createWithExtId (self, uid , extid , group ):
		postUri = "/{uid}/{extid}/createwithextid";
		data = None
		postUri = postUri.replace("{uid}",uid);
		postUri = postUri.replace("{extid}",extid);
		from netbluemind.group.api.Group import Group
		from netbluemind.group.api.Group import __GroupSerDer__
		data = __GroupSerDer__().encode(group)

		queryParams = {     };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getMembers (self, uid ):
		postUri = "/{uid}/members";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.group.api.Member import Member
		from netbluemind.group.api.Member import __MemberSerDer__
		return self.handleResult__(serder.ListSerDer(__MemberSerDer__()), response)
