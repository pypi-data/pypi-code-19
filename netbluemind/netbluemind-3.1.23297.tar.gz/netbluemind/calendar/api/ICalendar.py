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

class ICalendar(BaseEndpoint):
	def __init__(self, apiKey, url ,containerUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/calendars/{containerUid}'
		self.containerUid_ = containerUid
		self.base = self.base.replace('{containerUid}',containerUid)

	def update (self, uid , event , sendNotifications ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.calendar.api.VEventSeries import VEventSeries
		from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
		data = __VEventSeriesSerDer__().encode(event)

		queryParams = {    'sendNotifications': sendNotifications   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def updates (self, changes ):
		postUri = "/_mupdates";
		data = None
		from netbluemind.calendar.api.VEventChanges import VEventChanges
		from netbluemind.calendar.api.VEventChanges import __VEventChangesSerDer__
		data = __VEventChangesSerDer__().encode(changes)

		queryParams = {   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.container.model.ContainerUpdatesResult import ContainerUpdatesResult
		from netbluemind.core.container.model.ContainerUpdatesResult import __ContainerUpdatesResultSerDer__
		return self.handleResult__(__ContainerUpdatesResultSerDer__(), response)
	def delete (self, uid , sendNotifications ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   'sendNotifications': sendNotifications   };

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
		from netbluemind.calendar.api.VEventQuery import VEventQuery
		from netbluemind.calendar.api.VEventQuery import __VEventQuerySerDer__
		data = __VEventQuerySerDer__().encode(query)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.calendar.api.VEventSeries import VEventSeries
		from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		from netbluemind.core.api.ListResult import ListResult
		from netbluemind.core.api.ListResult import __ListResultSerDer__
		return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__VEventSeriesSerDer__())), response)
	def getReminder (self, dtalarm ):
		postUri = "/_remimder";
		data = None
		from netbluemind.core.api.date.BmDateTime import BmDateTime
		from netbluemind.core.api.date.BmDateTime import __BmDateTimeSerDer__
		data = __BmDateTimeSerDer__().encode(dtalarm)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.calendar.api.Reminder import Reminder
		from netbluemind.calendar.api.Reminder import __ReminderSerDer__
		return self.handleResult__(serder.ListSerDer(__ReminderSerDer__()), response)
	def create (self, uid , event , sendNotifications ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.calendar.api.VEventSeries import VEventSeries
		from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
		data = __VEventSeriesSerDer__().encode(event)

		queryParams = {    'sendNotifications': sendNotifications   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def all (self):
		postUri = "/_all";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ListSerDer(serder.STRING), response)
	def getVersion (self):
		postUri = "/_version";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.LONG, response)
	def multipleGet (self, uids ):
		postUri = "/_mget";
		data = None
		data = serder.ListSerDer(serder.STRING).encode(uids)

		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.calendar.api.VEventSeries import VEventSeries
		from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__VEventSeriesSerDer__())), response)
	def touch (self, uid ):
		postUri = "/{uid}/_touch";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def list (self):
		postUri = "/_list";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.calendar.api.VEventSeries import VEventSeries
		from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		from netbluemind.core.api.ListResult import ListResult
		from netbluemind.core.api.ListResult import __ListResultSerDer__
		return self.handleResult__(__ListResultSerDer__(__ItemValueSerDer__(__VEventSeriesSerDer__())), response)
	def sync (self, since , changes ):
		postUri = "/_sync";
		data = None
		from netbluemind.calendar.api.VEventChanges import VEventChanges
		from netbluemind.calendar.api.VEventChanges import __VEventChangesSerDer__
		data = __VEventChangesSerDer__().encode(changes)

		queryParams = {  'since': since    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
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
		from netbluemind.calendar.api.VEventSeries import VEventSeries
		from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__VEventSeriesSerDer__()), response)
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
	def createById (self, id , event , sendNotifications ):
		postUri = "/_byId";
		data = None
		from netbluemind.calendar.api.VEventSeries import VEventSeries
		from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
		data = __VEventSeriesSerDer__().encode(event)

		queryParams = {  'id': id   , 'sendNotifications': sendNotifications   };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getByIcsUid (self, uid ):
		postUri = "/_icsuid/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.calendar.api.VEventSeries import VEventSeries
		from netbluemind.calendar.api.VEventSeries import __VEventSeriesSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__VEventSeriesSerDer__())), response)
