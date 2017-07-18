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

class IServer(BaseEndpoint):
	def __init__(self, apiKey, url ,containerUid ):
		self.url = url
		self.apiKey = apiKey
		self.base = url +'/servers/{containerUid}'
		self.containerUid_ = containerUid
		self.base = self.base.replace('{containerUid}',containerUid)

	def submit (self, uid , command ):
		postUri = "/{uid}/submit_command";
		data = None
		postUri = postUri.replace("{uid}",uid);
		data = serder.STRING.encode(command)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.STRING, response)
	def update (self, uid , srv ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.server.api.Server import Server
		from netbluemind.server.api.Server import __ServerSerDer__
		data = __ServerSerDer__().encode(srv)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def getAssignments (self, domainUid ):
		postUri = "/{domainUid}/assignments";
		data = None
		postUri = postUri.replace("{domainUid}",domainUid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.server.api.Assignment import Assignment
		from netbluemind.server.api.Assignment import __AssignmentSerDer__
		return self.handleResult__(serder.ListSerDer(__AssignmentSerDer__()), response)
	def setTags (self, uid , tags ):
		postUri = "/{uid}/tags";
		data = None
		postUri = postUri.replace("{uid}",uid);
		data = serder.ListSerDer(serder.STRING).encode(tags)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def getStatus (self, uid , ref ):
		postUri = "/{uid}/command_status";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   'ref': ref   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.server.api.CommandStatus import CommandStatus
		from netbluemind.server.api.CommandStatus import __CommandStatusSerDer__
		return self.handleResult__(__CommandStatusSerDer__(), response)
	def delete (self, uid ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def byAssignment (self, domainUid , tag ):
		postUri = "/{domainUid}/byAssignment";
		data = None
		postUri = postUri.replace("{domainUid}",domainUid);
		queryParams = {   'tag': tag   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ListSerDer(serder.STRING), response)
	def create (self, uid , srv ):
		postUri = "/{uid}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		from netbluemind.server.api.Server import Server
		from netbluemind.server.api.Server import __ServerSerDer__
		data = __ServerSerDer__().encode(srv)

		queryParams = {    };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.core.task.api.TaskRef import TaskRef
		from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
		return self.handleResult__(__TaskRefSerDer__(), response)
	def allComplete (self):
		postUri = "/_complete";
		data = None
		queryParams = {  };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.server.api.Server import Server
		from netbluemind.server.api.Server import __ServerSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__ServerSerDer__())), response)
	def writeFile (self, uid , path , content ):
		postUri = "/{uid}/fs/{path}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		postUri = postUri.replace("{path}",path);
		data = serder.ByteArraySerDer.encode(content)

		queryParams = {     };

		response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def unassign (self, serverUid , domainUid , tag ):
		postUri = "/{domainUid}/assignments/{serverUid}/_unassign";
		data = None
		postUri = postUri.replace("{serverUid}",serverUid);
		postUri = postUri.replace("{domainUid}",domainUid);
		queryParams = {    'tag': tag   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
	def getComplete (self, uid ):
		postUri = "/{uid}/complete";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.server.api.Server import Server
		from netbluemind.server.api.Server import __ServerSerDer__
		from netbluemind.core.container.model.ItemValue import ItemValue
		from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
		return self.handleResult__(__ItemValueSerDer__(__ServerSerDer__()), response)
	def getServerAssignments (self, uid ):
		postUri = "/{uid}/serverAssignments";
		data = None
		postUri = postUri.replace("{uid}",uid);
		queryParams = {   };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.server.api.Assignment import Assignment
		from netbluemind.server.api.Assignment import __AssignmentSerDer__
		return self.handleResult__(serder.ListSerDer(__AssignmentSerDer__()), response)
	def readFile (self, uid , path ):
		postUri = "/{uid}/fs/{path}";
		data = None
		postUri = postUri.replace("{uid}",uid);
		postUri = postUri.replace("{path}",path);
		queryParams = {    };

		response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(serder.ByteArraySerDer, response)
	def submitAndWait (self, uid , command ):
		postUri = "/{uid}/submit_command_and_wait";
		data = None
		postUri = postUri.replace("{uid}",uid);
		data = serder.STRING.encode(command)

		queryParams = {    };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		from netbluemind.server.api.CommandStatus import CommandStatus
		from netbluemind.server.api.CommandStatus import __CommandStatusSerDer__
		return self.handleResult__(__CommandStatusSerDer__(), response)
	def assign (self, serverUid , domainUid , tag ):
		postUri = "/{domainUid}/assignments/{serverUid}/_assign";
		data = None
		postUri = postUri.replace("{serverUid}",serverUid);
		postUri = postUri.replace("{domainUid}",domainUid);
		queryParams = {    'tag': tag   };

		response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json'}, data = json.dumps(data));
		return self.handleResult__(None, response)
