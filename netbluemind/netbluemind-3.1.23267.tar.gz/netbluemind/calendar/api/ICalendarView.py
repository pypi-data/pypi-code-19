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

class ICalendarView(BaseEndpoint):
	def __init__(self, apiKey, url ,containerUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/calendars/view/{containerUid}'
		self.containerUid_ = containerUid
		self.base = self.base.replace('{containerUid}',containerUid)

	def multipleGet (self, uids ):
		postUri = "/_mget";
		data = None
		data = serder.ListSerDer(serder.STRING).encode(uids)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.calendar.api.CalendarView import CalendarView
		from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__CalendarViewSerDer__())), response)
	def update (self, uid , view ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.calendar.api.CalendarView import CalendarView
		from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
		data = __CalendarViewSerDer__().encode(view)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def list (self):
		postUri = "/_list";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.calendar.api.CalendarView import CalendarView
		from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		from netbluemind.core.api.ListResult import ListResult
		from netbluemind.core.api.ListResult import __ListResultSerDer__
		return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__CalendarViewSerDer__())), response)
	def updates (self, changes ):
		postUri = "/_mupdates";
		data = None
		from netbluemind.calendar.api.CalendarViewChanges import CalendarViewChanges
		from netbluemind.calendar.api.CalendarViewChanges import __CalendarViewChangesSerDer__
		data = __CalendarViewChangesSerDer__().encode(changes)

		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def delete (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def setDefault (self, uid ):
		postUri = "/{uid}/_asdefault";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def changeset (self, since ):
		postUri = "/_changeset";
		data = None
		queryParams = {  'since': since   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
		from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
		return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
	def getComplete (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.calendar.api.CalendarView import CalendarView
		from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__CalendarViewSerDer__()), response)
	def create (self, uid , view ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.calendar.api.CalendarView import CalendarView
		from netbluemind.calendar.api.CalendarView import __CalendarViewSerDer__
		data = __CalendarViewSerDer__().encode(view)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
