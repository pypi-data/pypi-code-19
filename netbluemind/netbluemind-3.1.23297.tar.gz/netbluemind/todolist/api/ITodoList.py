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

class ITodoList(BaseEndpoint):
	def __init__(self, apiKey, url ,containerUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/todolist/{containerUid}'
		self.containerUid_ = containerUid
		self.base = self.base.replace('{containerUid}',containerUid)

	def update (self, uid , todo ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.todolist.api.VTodo import VTodo
		from netbluemind.todolist.api.VTodo import __VTodoSerDer__
		data = __VTodoSerDer__().encode(todo)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def updates (self, changes ):
		postUri = "/_mupdates";
		data = None
		from netbluemind.todolist.api.VTodoChanges import VTodoChanges
		from netbluemind.todolist.api.VTodoChanges import __VTodoChangesSerDer__
		data = __VTodoChangesSerDer__().encode(changes)

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
		from netbluemind.todolist.api.VTodoQuery import VTodoQuery
		from netbluemind.todolist.api.VTodoQuery import __VTodoQuerySerDer__
		data = __VTodoQuerySerDer__().encode(query)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.todolist.api.VTodo import VTodo
		from netbluemind.todolist.api.VTodo import __VTodoSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		from netbluemind.core.api.ListResult import ListResult
		from netbluemind.core.api.ListResult import __ListResultSerDer__
		return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__VTodoSerDer__())), response)
	def getReminder (self, dtalarm ):
		postUri = "/_remimder";
		data = None
		from netbluemind.core.api.date.BmDateTime import BmDateTime
		from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
		data = __BmDateTimeSerDer__().encode(dtalarm)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.todolist.api.Reminder import Reminder
		from netbluemind.todolist.api.Reminder import __ReminderSerDer__
		return self.handleResult__(serder.ListSerDer(__ReminderSerDer__()), response)
	def create (self, uid , todo ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.todolist.api.VTodo import VTodo
		from netbluemind.todolist.api.VTodo import __VTodoSerDer__
		data = __VTodoSerDer__().encode(todo)

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
	def all (self):
		postUri = "";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.todolist.api.VTodo import VTodo
		from netbluemind.todolist.api.VTodo import __VTodoSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__VTodoSerDer__())), response)
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
		from netbluemind.todolist.api.VTodo import VTodo
		from netbluemind.todolist.api.VTodo import __VTodoSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__VTodoSerDer__())), response)
	def sync (self, since , changes ):
		postUri = "/_sync";
		data = None
		from netbluemind.todolist.api.VTodoChanges import VTodoChanges
		from netbluemind.todolist.api.VTodoChanges import __VTodoChangesSerDer__
		data = __VTodoChangesSerDer__().encode(changes)

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
	def getComplete (self, uid ):
		postUri = "/{uid}/complete";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.todolist.api.VTodo import VTodo
		from netbluemind.todolist.api.VTodo import __VTodoSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__VTodoSerDer__()), response)
	def containerChangelog (self, arg0 ):
		postUri = "/_changelog";
		data = None
		data = serder.LONG.encode(arg0)

		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerChangelog import ContainerChangelog
		from netbluemind.core.container.model.ContainerChangelog import __ContainerChangelogSerDer__
		return self.handleResult__(__ContainerChangelogSerDer__(), response)
	def reset (self):
		postUri = "/_reset";
		data = None
		queryParams = {  };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
