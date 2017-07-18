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

class IUser(BaseEndpoint):
	def __init__(self, apiKey, url ,domainUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/users/{domainUid}'
		self.domainUid_ = domainUid
		self.base = self.base.replace('{domainUid}',domainUid)

	def setPassword (self, uid , password ):
		postUri = "/{uid}/password_";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.user.api.ChangePassword import ChangePassword
		from netbluemind.user.api.ChangePassword import __ChangePasswordSerDer__
		data = __ChangePasswordSerDer__().encode(password)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getPhoto (self, uid ):
		postUri = "/{uid}/photo";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ByteArraySerDer, response)
	def allUids (self):
		postUri = "/_alluids";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ListSerDer(serder.STRING), response)
	def update (self, uid , user ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.user.api.User import User
		from netbluemind.user.api.User import __UserSerDer__
		data = __UserSerDer__().encode(user)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getVCard (self, uid ):
		postUri = "/{uid}/vcard";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.addressbook.api.VCard import VCard
		from netbluemind.addressbook.api.VCard import __VCardSerDer__
		return self.handleResult__(__VCardSerDer__(), response)
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
	def getResolvedRoles (self, uid ):
		postUri = "/{uid}/roles_resolved";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.SetSerDer(serder.STRING), response)
	def byLogin (self, login ):
		postUri = "/byLogin/{login}";
		data = None
		postUri = postUri.replace("{login}",login);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.user.api.User import User
		from netbluemind.user.api.User import __UserSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__UserSerDer__()), response)
	def byEmail (self, email ):
		postUri = "/byEmail/{email}";
		data = None
		postUri = postUri.replace("{email}",email);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.user.api.User import User
		from netbluemind.user.api.User import __UserSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__UserSerDer__()), response)
	def create (self, uid , user ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.user.api.User import User
		from netbluemind.user.api.User import __UserSerDer__
		data = __UserSerDer__().encode(user)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def memberOf (self, uid ):
		postUri = "/{uid}/groups";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.group.api.Group import Group
		from netbluemind.group.api.Group import __GroupSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__GroupSerDer__())), response)
	def memberOfGroups (self, uid ):
		postUri = "/{uid}/groupUids";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ListSerDer(serder.STRING), response)
	def setRoles (self, uid , roles ):
		postUri = "/{uid}/roles";
		data = None
		postUri = postUri.replace("{uid}",uid);
		data = serder.SetSerDer(serder.STRING).encode(roles)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getRoles (self, uid ):
		postUri = "/{uid}/roles";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.SetSerDer(serder.STRING), response)
	def updateVCard (self, uid , userVCard ):
		postUri = "/{uid}/vcard";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.addressbook.api.VCard import VCard
		from netbluemind.addressbook.api.VCard import __VCardSerDer__
		data = __VCardSerDer__().encode(userVCard)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def checkAll (self):
		postUri = "/_check-all";
		data = None
		queryParams = {  };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def byExtId (self, extid ):
		postUri = "/byExtId/{extid}";
		data = None
		postUri = postUri.replace("{extid}",extid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.user.api.User import User
		from netbluemind.user.api.User import __UserSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__UserSerDer__()), response)
	def checkAndRepair (self, uid ):
		postUri = "/{uid}/_check-and-repair";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def check (self, uid ):
		postUri = "/{uid}/_check";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
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
		from netbluemind.user.api.User import User
		from netbluemind.user.api.User import __UserSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__UserSerDer__()), response)
	def setPhoto (self, uid , photo ):
		postUri = "/{uid}/photo";
		data = None
		postUri = postUri.replace("{uid}",uid);
		data = serder.ByteArraySerDer.encode(photo)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getUsersWithRoles (self, roles ):
		postUri = "/_roleusers";
		data = None
		data = serder.ListSerDer(serder.STRING).encode(roles)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.SetSerDer(serder.STRING), response)
	def createWithExtId (self, uid , extid , user ):
		postUri = "/{uid}/{extid}/createwithextid";
		data = None
		postUri = postUri.replace("{uid}",uid);
		postUri = postUri.replace("{extid}",extid);
		from netbluemind.user.api.User import User
		from netbluemind.user.api.User import __UserSerDer__
		data = __UserSerDer__().encode(user)

		queryParams = {     };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def checkAndRepairAll (self):
		postUri = "/_check-and-repair-all";
		data = None
		queryParams = {  };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
